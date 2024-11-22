#include <unistd.h>
#include <fcntl.h>
#include <syslog.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int usbtmc;

int main()
{   
    int ret;
    char s[1024];

    usbtmc = open("/dev/usbtmc0", O_RDWR);

        float R;

        sprintf(s,"MEAS:RES?\r\n");
	    ret = write(usbtmc,s,strlen(s));
	    if (ret < 0) fprintf(stderr,"sending MEAS:RES? command to akip  failed %d\n",ret);
        
        ret = read(usbtmc,s,1000);
	    if (ret < 0) fprintf(stderr,"receiving MEAS:RES? command response failed %d\n",ret);
        R = atof(s);

        float t = (R/10000.-1)/0.003850;
        //sprintf(s,"%.2f\n",t);
        //printf("%s\n",s);

	time_t result = time(0);
	sprintf(s,"%ld %.2f",result, t);
        printf("%s\n",s);
	//cout << result << " seconds since the Epoch\n";


    exit(0);
}
