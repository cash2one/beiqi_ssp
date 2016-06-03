#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "qisr.h"
#include "qtts.h"
#include "msp_cmn.h"
#include "msp_errors.h"


// 最大语音文件输出大小500k
#define	MAX_WAV_SIZE	(500 * 1024)

#define	BUFFER_SIZE	4096
#define FRAME_LEN	640 
#define HINTS_SIZE  100


const char*		G_SZ_V2TSessionID					=	NULL;		//  语音转文本session ID
const char*		G_SZ_T2VSessionID					=	NULL;		//  文本转语音session ID
char			G_SZ_RecResult[BUFFER_SIZE]			=	{NULL};		//	语音识别文本字符串
char			G_SZ_EndHints[HINTS_SIZE]			=	{NULL};		//	G_SZ_EndHints为结束本次会话的原因描述，由用户自定义
static char		G_SZ_ComVoiceData[MAX_WAV_SIZE]		=	{NULL};		//  文本合成语音二进制流
const char*		G_SZ_V2TSessionParams				=	"sub = iat, domain = iat, language = zh_ch, accent = mandarin, sample_rate = 16000, result_type = plain, result_encoding = utf8";
const char*		G_SZ_T2VSessionParams				=	"voice_name = xiaoyan, text_encoding = UTF8, sample_rate = 16000, speed = 50, volume = 50, pitch = 50, rdn = 2";



/* wav音频头部格式 */
typedef struct _wave_pcm_hdr
{
	char			riff[4];                // = "RIFF"
	int				size_8;                 // = FileSize - 8
	char			wave[4];                // = "WAVE"
	char			fmt[4];                 // = "fmt "
	int				fmt_size;				// = 下一个结构体的大小 : 16

	short int		format_tag;             // = PCM : 1
	short int       channels;               // = 通道数 : 1
	int				samples_per_sec;        // = 采样率 : 8000 | 6000 | 11025 | 16000
	int				avg_bytes_per_sec;      // = 每秒字节数 : samples_per_sec * bits_per_sample / 8
	short int       block_align;            // = 每采样点字节数 : wBitsPerSample / 8
	short int       bits_per_sample;        // = 量化比特数: 8 | 16

	char            data[4];                // = "data";
	int		data_size;						// = 纯数据长度 : FileSize - 44 
} wave_pcm_hdr;

/* 默认wav音频头部数据 */
wave_pcm_hdr default_wav_hdr = 
{
	{ 'R', 'I', 'F', 'F' },
	0,
	{'W', 'A', 'V', 'E'},
	{'f', 'm', 't', ' '},
	16,
	1,
	1,
	16000,
	32000,
	2,
	16,
	{'d', 'a', 't', 'a'},
	0  
};


/** 
 *  上传用户词表
 *   
 *  @return 上传的错误码
 */  
int __upload_userwords()
{
	char*			userwords	=	NULL;
	unsigned int	len			=	0;
	unsigned int	read_len	=	0;
	FILE*			fp			=	NULL;
	int				ret			=	-1;

	fp = fopen("userwords.txt", "rb");
	if (NULL == fp)										
	{
		printf("\nopen [userwords.txt] failed! \n");
		goto upload_exit;
	}

	fseek(fp, 0, SEEK_END);
	len = ftell(fp); //获取音频文件大小
	fseek(fp, 0, SEEK_SET);  					
	
	userwords = (char*)malloc(len + 1);
	if (NULL == userwords)
	{
		printf("\nout of memory! \n");
		goto upload_exit;
	}

	read_len = fread((void*)userwords, 1, len, fp); //读取用户词表内容
	if (read_len != len)
	{
		printf("\nread [userwords.txt] failed!\n");
		goto upload_exit;
	}
	userwords[len] = '\0';
	
	MSPUploadData("userwords", userwords, len, "sub = uup, dtt = userword", &ret); //上传用户词表
	if (MSP_SUCCESS != ret)
	{
		printf("\nMSPUploadData failed ! errorCode: %d \n", ret);
		goto upload_exit;
	}
	
upload_exit:
	if (NULL != fp)
	{
		fclose(fp);
		fp = NULL;
	}	
	if (NULL != userwords)
	{
		free(userwords);
		userwords = NULL;
	}
	return ret;
}


/** 
 *  语音转文字处理函数： 音频文件一次性写入
 *  @param p_voice_data ： 音频二进制流
 *  @param l_voice_size ： 音频二进制流长度 
 *   
 *  @return 识别到的文本字符串
 */  
char* __voice2text_all_proc(const char* p_voice_data, long l_voice_size)
{
	unsigned int	total_len					=	0; 
	int				ep_stat						=	MSP_EP_LOOKING_FOR_SPEECH;		//端点检测
	int				rec_stat					=	MSP_REC_STATUS_SUCCESS ;		//识别状态
	int				errcode						=	MSP_SUCCESS ;
	int				ret							=	0;

	memset(G_SZ_RecResult,0, BUFFER_SIZE);
	memset(G_SZ_EndHints, 0, HINTS_SIZE);

	ret = QISRAudioWrite(G_SZ_V2TSessionID, p_voice_data, l_voice_size, MSP_AUDIO_SAMPLE_LAST, &ep_stat, &rec_stat);
	if (MSP_SUCCESS != ret)
	{
		printf("\nQISRAudioWrite failed! error code:%d\n", ret);
		goto iat_exit;
	}

	while (MSP_REC_STATUS_COMPLETE != rec_stat) 
	{
		const char *rslt = QISRGetResult(G_SZ_V2TSessionID, &rec_stat, 0, &errcode);
		if (MSP_SUCCESS != errcode)
		{
			printf("\nQISRGetResult failed, error code: %d\n", errcode);
			goto iat_exit;
		}
		if (NULL != rslt)
		{
			unsigned int rslt_len = strlen(rslt);
			total_len += rslt_len;
			if (total_len >= BUFFER_SIZE)
			{
				printf("\nno enough buffer for G_SZ_RecResult !\n");
				goto iat_exit;
			}
			strncat(G_SZ_RecResult, rslt, rslt_len);
		}
	}
	return G_SZ_RecResult;

iat_exit:
	return "";
}


/** 
 *  语音转文字处理函数：每次写入200ms音频
 *  @param p_voice_data ： 音频二进制流
 *  @param l_voice_size ： 音频二进制流长度 
 *   
 *  @return 识别到的文本字符串
 */  
char* __voice2text_proc(const char* p_voice_data, long l_voice_size)
{
	unsigned int	total_len					=	0; 
	int				aud_stat					=	MSP_AUDIO_SAMPLE_CONTINUE ;		//音频状态
	int				ep_stat						=	MSP_EP_LOOKING_FOR_SPEECH;		//端点检测
	int				rec_stat					=	MSP_REC_STATUS_SUCCESS ;		//识别状态
	int				errcode						=	MSP_SUCCESS ;
	long			pcm_count					=	0;

	memset(G_SZ_RecResult,0, BUFFER_SIZE);
	memset(G_SZ_EndHints, 0, HINTS_SIZE);
	
	while (1) 
	{
		unsigned int len = 10 * FRAME_LEN; // 每次写入200ms音频(16k，16bit)：1帧音频20ms，10帧=200ms。16k采样率的16位音频，一帧的大小为640Byte
		int ret = 0;

		if (l_voice_size < 2 * len) 
			len = l_voice_size;
		if (len <= 0)
			break;

		aud_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		if (0 == pcm_count)
			aud_stat = MSP_AUDIO_SAMPLE_FIRST;

		ret = QISRAudioWrite(G_SZ_V2TSessionID, (const void *)&p_voice_data[pcm_count], len, aud_stat, &ep_stat, &rec_stat);
		if (MSP_SUCCESS != ret)
		{
			printf("\nQISRAudioWrite failed! error code:%d\n", ret);
			goto iat_exit;
		}
			
		pcm_count += (long)len;
		l_voice_size  -= (long)len;
		
		if (MSP_REC_STATUS_SUCCESS == rec_stat) //已经有部分听写结果
		{
			const char *rslt = QISRGetResult(G_SZ_V2TSessionID, &rec_stat, 0, &errcode);
			if (MSP_SUCCESS != errcode)
			{
				printf("\nQISRGetResult failed! error code: %d\n", errcode);
				goto iat_exit;
			}
			if (NULL != rslt)
			{
				unsigned int rslt_len = strlen(rslt);
				total_len += rslt_len;
				if (total_len >= BUFFER_SIZE)
				{
					printf("\nno enough buffer for G_SZ_RecResult !\n");
					goto iat_exit;
				}
				strncat(G_SZ_RecResult, rslt, rslt_len);
			}
		}

		if (MSP_EP_AFTER_SPEECH == ep_stat)
			break;
	}
	errcode = QISRAudioWrite(G_SZ_V2TSessionID, NULL, 0, MSP_AUDIO_SAMPLE_LAST, &ep_stat, &rec_stat);
	if (MSP_SUCCESS != errcode)
	{
		printf("\nQISRAudioWrite failed! error code:%d \n", errcode);
		goto iat_exit;	
	}

	while (MSP_REC_STATUS_COMPLETE != rec_stat) 
	{
		const char *rslt = QISRGetResult(G_SZ_V2TSessionID, &rec_stat, 0, &errcode);
		if (MSP_SUCCESS != errcode)
		{
			printf("\nQISRGetResult failed, error code: %d\n", errcode);
			goto iat_exit;
		}
		if (NULL != rslt)
		{
			unsigned int rslt_len = strlen(rslt);
			total_len += rslt_len;
			if (total_len >= BUFFER_SIZE)
			{
				printf("\nno enough buffer for G_SZ_RecResult !\n");
				goto iat_exit;
			}
			strncat(G_SZ_RecResult, rslt, rslt_len);
		}
	}
	return G_SZ_RecResult;

iat_exit:
	return "";
}


/** 
 *  文本转语音处理函数: 返回字符串，但是python接收会转成字符串，截断二进制流，这边还需要处理下
 *  @param p_text ： 文本字符串
 *   
 *  @return 合成的音频二进制流
 */ 
char* __text2voice_proc(const char* p_text)
{
	int          ret			= -1;
	const char*  sessionID		= NULL;
	unsigned int audio_len		= 0;
	int          synth_status	= MSP_TTS_FLAG_STILL_HAVE_DATA;
	wave_pcm_hdr wav_hdr		= default_wav_hdr;
	int			 n_voice_len	= 0;

	memset(G_SZ_ComVoiceData, 0, MAX_WAV_SIZE);

	if (NULL == p_text)
	{
		return "";
	}

	/* 开始合成 */
	ret = QTTSTextPut(G_SZ_T2VSessionID, p_text, (unsigned int)strlen(p_text), NULL);
	if (MSP_SUCCESS != ret)
	{
		printf("QTTSTextPut failed, error code: %d.\n",ret);
		return "";
	}

	//添加wav音频头，使用采样率为16000
	memcpy(G_SZ_ComVoiceData, &wav_hdr, sizeof(wav_hdr));
	n_voice_len += sizeof(wav_hdr); 

	while (1) 
	{
		/* 获取合成音频 */
		const void* data = QTTSAudioGet(G_SZ_T2VSessionID, &audio_len, &synth_status, &ret);
		if (MSP_SUCCESS != ret)
			break;
		if (NULL != data)
		{
			memcpy(&G_SZ_ComVoiceData[n_voice_len], data, audio_len);
			n_voice_len += audio_len;

		    wav_hdr.data_size += audio_len; //计算data_size大小
		}
		if (MSP_TTS_FLAG_DATA_END == synth_status)
			break;
	}
	if (MSP_SUCCESS != ret)
	{
		printf("QTTSAudioGet failed, error code: %d.\n",ret);
		return "";
	}
	/* 修正wav文件头数据的大小 */
	wav_hdr.size_8 += wav_hdr.data_size + (sizeof(wav_hdr) - 8);
	
	/* 将修正过的数据写回文件头部,音频文件为wav格式 */
	memcpy(G_SZ_ComVoiceData+4, &wav_hdr.size_8, sizeof(wav_hdr.size_8));//写入size_8的值
	memcpy(G_SZ_ComVoiceData+40, &wav_hdr.data_size, sizeof(wav_hdr.data_size));//写入data_size的值
	return G_SZ_ComVoiceData;
}



/** 
 *  msp登录, 对外
 *  @param appid ： 产品的appid,appid与msc库绑定,请勿随意改动
 *   
 *  @return 错误码
 */ 
int msp_login(const char* appid)
{
	int ret = MSP_SUCCESS;

	char login_params[ 50];
	sprintf( login_params , "appid = %s, work_dir = ." , appid);
	

	ret = MSPLogin(NULL, NULL, login_params);//第一个参数是用户名，第二个参数是密码，第三个参数是登录参数，用户名和密码可在http://open.voicecloud.cn注册获取
	if (MSP_SUCCESS != ret)
	{
		printf("MSPLogin failed, error code: %d.\n", ret);
	}
	return ret;
}


/** 
 *  msp退出登录, 对外
 *   
 */ 
void msp_logout()
{
	MSPLogout();
}


/** 
 *  音频转文字session开始, 对外,目前发现科大讯飞无法在同一个session多次处理
 *   
 *  @return 错误码
 */ 
int session_v2t_start()
{
	int				ret						=	MSP_SUCCESS ;
	/*
	* rdn:           合成音频数字发音方式
	* volume:        合成音频的音量
	* pitch:         合成音频的音调
	* speed:         合成音频对应的语速
	* voice_name:    合成发音人
	* sample_rate:   合成音频采样率
	* text_encoding: 合成文本编码格式
	*
	* 详细参数说明请参阅《iFlytek MSC Reference Manual》
	*/
	G_SZ_V2TSessionID = QISRSessionBegin(NULL, G_SZ_V2TSessionParams, &ret); //听写不需要语法，第一个参数为NULL
	if (MSP_SUCCESS != ret)
	{
		printf("\nQISRSessionBegin failed! error code:%d\n", ret);
	}	
	return ret;
}


/** 
 *  音频转文字session结束, 对外
 *   
 *  @return 错误码
 */ 
int session_v2t_end()
{
	int         ret          = -1;
	ret = QISRSessionEnd(G_SZ_V2TSessionID, G_SZ_EndHints);
	if (MSP_SUCCESS != ret)
	{
		printf("QTTSSessionEnd failed, error code: %d.\n",ret);
	}
	return ret;
}


/** 
 *  文字转音频session开始, 对外,目前发现科大讯飞无法在同一个session多次处理
 *   
 *  @return 错误码
 */ 
int session_t2v_start()
{
	int          ret          = -1;

	/*
	* rdn:           合成音频数字发音方式
	* volume:        合成音频的音量
	* pitch:         合成音频的音调
	* speed:         合成音频对应的语速
	* voice_name:    合成发音人
	* sample_rate:   合成音频采样率
	* text_encoding: 合成文本编码格式
	*
	* 详细参数说明请参阅《iFlytek MSC Reference Manual》
	*/
	G_SZ_T2VSessionID = QTTSSessionBegin(G_SZ_T2VSessionParams, &ret);
	if (MSP_SUCCESS != ret)
	{
		printf("QTTSSessionBegin failed, error code: %d.\n", ret);
	}
	
	return ret;
}


/** 
 *  文字转音频session结束, 对外
 *   
 *  @return 错误码
 */ 
int session_t2v_end()
{
	int          ret          = -1;
	ret = QTTSSessionEnd(G_SZ_T2VSessionID, "Normal");
	if (MSP_SUCCESS != ret)
	{
		printf("QTTSSessionEnd failed, error code: %d.\n",ret);
	}
	return ret;
}


/** 
 *  文本转语音接口，对外
 *  @param text ： 文本字符串
 *   
 *  @return 语音二进制流
 */ 
char* text_2_voice(const char* text)
{
	char*  p_voice_data = NULL;
	session_t2v_start();
	p_voice_data = __text2voice_proc(text);
	session_t2v_end();
	return p_voice_data;
}


/** 
 *  音频转文字接口，对外
 *  @param p_voice_data ： 语音二进制流
 *  @param l_voice_size ： 语音二进制流长度
 *  @param upload_on:	是否上传用户词表，默认不上传
 *   
 *  @return 文本字符串
 */ 
char* voice_2_text(const char* p_voice_data, long l_voice_size, int upload_on)
{
	int		ret		=	MSP_SUCCESS;
	char*	text	=	NULL;

	session_v2t_start();

	// 上传用户词表
	if (upload_on)
	{
		ret = __upload_userwords();
		if (MSP_SUCCESS != ret)
			return "";	
	}
	text = __voice2text_proc(p_voice_data, l_voice_size); //iflytek02音频内容为“中美数控”；如果上传了用户词表，识别结果为：“中美速控”。

	session_v2t_end();
	return text;
}


/** 
 *  加载指定音频数据，用于测试
 *  @param p_voice_path ： 音频文件路径
 *   
 *  @return 音频二进制流
 */
char* __load_voice_data(const char* p_voice_path)
{
	char*	p_voice_data	=	NULL;
	FILE*	f_pcm			=	NULL;
	long	l_read_size		=	0;
	long	l_voice_size	=	0;

	f_pcm = fopen(p_voice_path, "rb");
	if (NULL == f_pcm) 
	{
		printf("\nopen [%s] failed! \n", p_voice_path);
	}

	fseek(f_pcm, 0, SEEK_END);
	l_voice_size = ftell(f_pcm); //获取音频文件大小 
	fseek(f_pcm, 0, SEEK_SET);	

	p_voice_data = (char *)malloc(l_voice_size);
	if (NULL == p_voice_data)
	{
		printf("\nout of memory! \n");
	}
	l_read_size = fread((void *)p_voice_data, 1, l_voice_size, f_pcm); //读取音频文件内容
	return p_voice_data;
}


/** 
 *  保存音频数据到指定位置，用于测试
 *  @param p_voice_data ： 音频二进制数据
 *  @param p_voice_path ： 音频文件路径
 *   
 *  @return 音频二进制流
 */
void __save_voice_data(const char* p_voice_data,const char* p_voice_path)
{
	FILE*   fp = NULL;

	fp = fopen(p_voice_path, "wb");
	fwrite(p_voice_data, MAX_WAV_SIZE , 1, fp);
	fclose(fp);
	fp = NULL;
}


/** 
 *  测试主函数
 */
int main(int argc, char* argv[])
{
	char*			G_SZ_RecResult		=   NULL;
	int				upload_on		=	0;
	char*			szdata1			=	NULL;
	char*			szdata2			=	NULL;
	int				l_voice_size	=	148220; 	
	int				nloop			=	10;
	int				i				=	0;
	const char*		p_voice_path	=	"wav/iflytek02.wav";
	const char*		p_voice_data	=	NULL;
	const char*		filename		=	"tts_sample.wav"; //合成的语音文件名称
	const char*		appid			=	"57456239";
	const char*		text			=	"股票代码你想要吗"; //合成文本

	msp_login(appid);

	for(i=0;i<nloop;i++)
	{
		G_SZ_RecResult = voice_2_text(__load_voice_data(p_voice_path), l_voice_size, upload_on);
		printf("%s\n",G_SZ_RecResult);
	}
	

	for(i=0;i<nloop;i++)
	{
		p_voice_data = text_2_voice(text);
		__save_voice_data(p_voice_data, filename);
		printf("%d\n", i);
	}

	msp_logout();
}




