#include <errno.h>
#include <unistd.h>
#include <ctype.h>
#include <sys/ioctl.h>
#include <sys/termios.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/select.h>
#include <fcntl.h>
#include <syslog.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <signal.h>

//23.1   23.4

int usbtmc;
int tti0;
int PSchannel = 2;
void handler(int signum)
{
	printf("\n");
	printf("Aborted by user (ctrl-c)\n"); 
    printf("Be careful. Prototype is not supervised from now on.\n"); 
 //   printf("A defect in the Lauda chiller will lead to permanent Peltier damage.\n");
    printf("\n");

    syslog(LOG_INFO,"Aborted by user (ctrl-c)");
    closelog();

    exit(-1); 
}

void power_off()
{
    char s[1024];
    int ret;
 
    printf("Switch on peltier power supply ...\n");
    sprintf(s,"OP1 0\r\n");
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending switch off command to peltier PS failed %d\n",ret);   

    sprintf(s,"OP2 0\r\n");
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending switch off command to peltier PS failed %d\n",ret);   
}

void power_on() {
    char s[1024];
    int ret;
 
    printf("Switch on peltier power supply ...\n");
    sprintf(s,"OP1 1\r\n");
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending switch on command to peltier PS failed %d\n",ret);   

    sprintf(s,"OP2 1\r\n");
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending switch on command to peltier PS failed %d\n",ret);   
 
} 

void setpowerparametr(float uPS, float iPS, float uA, float iA )
{
    char s[1024];
    int ret;
   
    printf("set PS peltier parameters ...\n");
    sprintf(s,"V1 %.2f\r\n",uPS);
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending V1 command to TTi 0 failed %d\n",ret);
    
    sprintf(s,"I1 %.2f\r\n",iPS);
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending I1 command to TTi 0 failed %d\n",ret);
        
    sprintf(s,"V2 %.2f\r\n",uA);
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending V2 command to TTi 0 failed %d\n",ret);
    
    sprintf(s,"I2 %.2f\r\n",iA);
    ret = write(tti0,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending I2 command to TTi 0 failed %d\n",ret);
}


//int notif_sent_flag=0;



/*void emergency_power_off(char *reason)
{
    char s[1024];
    int ret;
    
    sprintf(s,"OUT0\r\n");
    ret = write(ttyUSB,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending switch off command to instek failed %d\n",ret);

    
    syslog(LOG_ALERT,"!!!!!!!!!!!!! COOLING PROBLEM DETECTED !!!!!!!!!!!!");
    syslog(LOG_ALERT,"!!!!!!!!!!!!! SWITCHING PELTIER POWER SUPPLY OFF !!!!!!!!!!!!");

    printf("!!!!!!!!!!!!! COOLING PROBLEM DETECTED !!!!!!!!!!!!\n");
    printf("!!!!!!!!!!!!! SWITCHING PELTIER POWER SUPPLY OFF !!!!!!!!!!!!\n");

    syslog(LOG_ALERT,"REASON: %s",reason);
    printf("REASON: %s\n",reason);


    exit(-1); 
}
*/


int main(int argc, char *argv[])
{
    
    float tmax = 26;
    float tmin = 24;
    float iPSmax = 2.;
    float iPSmin = 0.1;
    float uPS = 7.9;
    float iPS = 0.1;
    float uA = 5.4;
    float iA = 0.1;
    
    float uPScheck, iPScheck;

    signal(SIGINT, handler);      

/* load the driver for the power supplies */

    //system("modprobe usbserial vendor=0x103E product=0x0460");
   
/* open the links to the peltier & amplifire power supplies */
/* //    printf("Open link to peltier PS unit 0...\n");!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    tti0 = open("/dev/ttyACM0",O_RDWR);

    if (tti0 < 0) {
        fprintf(stderr,"cannot open serial link to the peltier power supply 0\n");
        exit(-1);
    }
    struct termios newtio;
    tcflush(tti0, TCIOFLUSH);
    if (tcgetattr(tti0, &newtio)!=0) printf("tcgetattr failed\n");

    speed_t _baud=B9600;_baud=B9600;
    cfsetospeed(&newtio, (speed_t)_baud);
    cfsetispeed(&newtio, (speed_t)_baud);
    newtio.c_cflag = (newtio.c_cflag & ~CSIZE) | CS8;
    newtio.c_cflag |= CLOCAL | CREAD;
    newtio.c_cflag &= ~(PARENB | PARODD);
    newtio.c_cflag &= ~CSTOPB;
    newtio.c_iflag=IGNBRK;
    newtio.c_lflag=0;
    newtio.c_oflag=0;
    newtio.c_cc[VTIME]=1;
    newtio.c_cc[VMIN]=60;
    if (tcsetattr(tti0, TCSANOW, &newtio)!=0) printf("tcsetattr  failed\n");
    int mcs=0;
    ioctl(tti0, TIOCMGET, &mcs);
    mcs |= TIOCM_RTS;
    ioctl(tti0, TIOCMSET, &mcs);

    if (tcgetattr(tti0, &newtio)!=0) printf("tcgetattr 2 failed\n");

    newtio.c_cflag |= CRTSCTS;
    if (tcsetattr(tti0, TCSANOW, &newtio)!=0) printf("tcsetattr 2 failed\n");
   
*/ //   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   
   
    
    int ret;
    char s[1024], stat[1024];
  //  printf("\n\nTemperature range = %.2f..%.2f°C, set peltier power supply current %.2fA\n\n",tmin,tmax,iPS);

/* open the links to the  akip voltmetr */
   // printf("Open link to akip ...\n");
    usbtmc = open("/dev/usbtmc0", O_RDWR);
    if (usbtmc < 0) {
        fprintf(stderr, "cannot open serial link to AKIP\n");
        exit(-1);
    }
 
        
/* set power supply parameters */
//    setpowerparametr(uPS, iPS, uA, iA); !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//    printf("Done    \n");
 

/*SWITCH ON PS peltier*/   
//    power_on(); !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//    printf("Done    \n");
    
/* control loop */
  //  printf("Starting control loop...\n");
//    while(1) {  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        float t, R, tR;
       
/* temperature measuremetns */
/*
//термопара     
        sprintf(s,"MEAS:TCO?\r\n");
	    ret = write(usbtmc,s,strlen(s));
	    if (ret < 0) fprintf(stderr,"sending MEAS:TCO? command to akip  failed %d\n",ret);
        
        ret = read(usbtmc,s,1000);
	    if (ret < 0) fprintf(stderr,"receiving MEAS:TCO? command response failed %d\n",ret);
        t = atof(s);
*/
//терморезистор
        sprintf(s,"MEAS:RES?\r\n");
	    ret = write(usbtmc,s,strlen(s));
	    if (ret < 0) fprintf(stderr,"sending MEAS:RES? command to akip  failed %d\n",ret);
        
        ret = read(usbtmc,s,1000);
	    if (ret < 0) fprintf(stderr,"receiving MEAS:RES? command response failed %d\n",ret);
        R = atof(s);




/* PS peltier status */
/*//read voltage 
        sprintf(s,"VSET%u?\r\n",PSchannel);
        ret = write(ttyUSB,s,strlen(s));
        if (ret < 0) fprintf(stderr,"sending VSET? command to instek failed %d\n",ret);

        ret = read(ttyUSB,s,1000);
        if (ret < 0) fprintf(stderr,"receiving VSET? command response failed %d\n",ret);
        uPScheck = atof(s);    
//read current     
        sprintf(s,"ISET%u?\r\n",PSchannel);
        ret = write(ttyUSB,s,strlen(s));
        if (ret < 0) fprintf(stderr,"sending ISET? command to instek failed %d\n",ret);

        ret = read(ttyUSB,s,1000);
        if (ret < 0) fprintf(stderr,"receiving ISET? command response failed %d\n",ret);
        iPScheck = atof(s);    
*/
        /* logfile */

        //sprintf(s,"resistance R = %.2fOm\n",R);
        //sprintf(s,"%.2f\n",R);

	/*
        sprintf(s,"%.2f\n",t);
        syslog(LOG_INFO,"%s",s);
        printf("%s\n",s);
	*/

        float t2 = (R/10000.-1)/0.003850;
        //float t2 = -261.502 + 0.0261611*R;
        sprintf(s,"%.2f\n",t2);
        syslog(LOG_INFO,"%s",s);
        printf("%s\n",s);

/*        
        sprintf(s,"PS INSTEK STATUS:  %.2fV / %.2fA\n",uPScheck,iPScheck);
        syslog(LOG_INFO,"%s",s);
        printf("%s\n",s);
*/

/*
        if (t>tmax) {
            iPS=iPS+0.2;
            if (iPS>=iPSmax) emergency_power_off("CAN'T CONTROL TEMPERATURE, SOMETHING WRIONG!");
        } 
        if (t<tmin) {
            iPS=iPS-0.2;
            if (iPS<0) iPS=0;
            if (iPS<=iPSmin) emergency_power_off("CAN'T CONTROL TEMPERATURE, SOMETHING WRIONG!");
        } 
        sprintf(s,"ISET%u:%.2f\r\n",PSchannel,iPS);
        ret = write(ttyUSB,s,strlen(s));
        if (ret < 0) fprintf(stderr,"sending ISET command to instek failed %d\n",ret);

        printf("wating 10 seconds ...\n");
        sleep(10);
*/        
//    }   
    
    /* read instek power supply parameters */
/*    printf("read instek power supply parameters ...\n");
    sprintf(s,"VSET%u?\r\n",PSchannel);
    ret = write(ttyUSB,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending VSET? command to instek failed %d\n",ret);

    ret = read(ttyUSB,s,1000);
    if (ret < 0) fprintf(stderr,"receiving VSET? command response failed %d\n",ret);
    uPScheck = atof(s);    
    
    sprintf(s,"ISET%u?\r\n",PSchannel);
    ret = write(ttyUSB,s,strlen(s));
    if (ret < 0) fprintf(stderr,"sending ISET? command to instek failed %d\n",ret);

    ret = read(ttyUSB,s,1000);
    if (ret < 0) fprintf(stderr,"receiving ISET? command response failed %d\n",ret);
    iPScheck = atof(s);    
       
    //if ( iPS != iPScheck  || iPS != iPScheck ) {

        /* re-read to make sure we do not switch off too early */
/*  
sleep(4);   
          
         sprintf(s,"ISET2?\n");
	 ret = write(ttyUSB,s,strlen(s));
	 if (ret < 0) fprintf(stderr,"sending MEAS:TCO? command to akip  failed %d\n",ret);

     ret = read(ttyUSB,s,1000);
	 if (ret < 0) fprintf(stderr,"receiving MEAS:TCO? command response failed %d\n",ret);
	 sscanf(s,"%f",&iPScheck);

     //sprintf(s,"t=%.2f ",iPScheck);

//
        sleep(6);   
   //
   //     sprintf(s,"VSET1?\n");
//	    ret = write(ttyUSB,s,strlen(s));
//	    if (ret < 0) fprintf(stderr,"sending VSET?  command to instek  instek %d\n",ret);
  //      
  //      ret = read(ttyUSB,s,1000);
//	    if (ret < 0) fprintf(stderr,"receiving VSET? command response failed %d\n",ret);
//	    sscanf(s,"%f",&uPScheck);


    
*/
   //  printf("%s\n",s);  
          
            
      //  sprintf(s,"ISET2?\r\n");
       // ret = write(ttyUSB,s,strlen(s));
        //if (ret < 0) fprintf(stderr,"sending ISET? command to instek failed %d\n",ret);

       // ret = read(ttyUSB,s,1000);
        //if (ret < 0) fprintf(stderr,"receiving ISET? command response failed %d\n",ret);
            
	    //sscanf(s,"%f",&iPScheck);

        //printf("uPS = %.5f  uPScheck = %.5f\n",uPS, uPScheck);
        //printf("iPS = %.5f  iPScheck = %.5f\n",iPS, iPScheck);
        //if ( iPS != iPScheck  || uPS != uPScheck ) emergency_power_off("CAN'T SET PS PARAMETRS");
        
       // exit(0);
    //}     

       
       


    exit(0);
}



