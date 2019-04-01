#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>

#define PORT 20100
#define SERVERS 5

void * server_thread(void *arg)
{

        int server_port = *((int *) arg);
        char message[1024];
        char buffer[1024];
        int opt = 1;
        struct sockaddr_in server_addr;
        int sock = 0, valread;
        int new_socket;
        struct sockaddr_in proxyserver_addr;

        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
        {
                printf("\nSocket creation error \n");
        }

        // This is to lose the pesky "Address already in use" error message
        if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                       &opt, sizeof(opt)))                                // SOL_SOCKET is the socket layer itself
        {
                perror("setsockopt");
        }

        memset(&proxyserver_addr, '0', sizeof(proxyserver_addr)); // to make sure the struct is empty. Essentially sets sin_zero as 0
        // which is meant to be, and rest is defined below

        proxyserver_addr.sin_family = AF_INET;
        proxyserver_addr.sin_port = htons(PORT);

        // Converts an IP address in numbers-and-dots notation into either a
        // struct in_addr or a struct in6_addr depending on whether you specify AF_INET or AF_INET6.
        if(inet_pton(AF_INET, "127.0.0.1", &proxyserver_addr.sin_addr)<=0)
        {
                printf("\nInvalid address/ Address not supported \n");
                // pthread_exit(NULL);
        }

        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(server_port);

        // Forcefully attaching socket to its respective port
        if (bind(sock, (struct sockaddr *)&server_addr,
                 sizeof(server_addr))<0)
        {
                perror("bind failed");
                exit(EXIT_FAILURE);
        }

        // Port bind is done. You want to wait for incoming connections and handle them in some way.
        // The process is two step: first you listen(), then you accept()
        if (listen(sock, 3) < 0) // 3 is the maximum size of queue - connections you haven't accepted
        {
                perror("listen");
                exit(EXIT_FAILURE);
        }

        addrlen = sizeof(server_addr);

        printf("Waiting for connections ...\n");

        while(1)
        {
                if ((new_socket = accept(sock, (struct sockaddr *)&proxyserver_addr, (socklen_t*)&addrlen))<0)
                {
                        perror("accept");
                        exit(EXIT_FAILURE);
                }

                char ip[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &(proxyserver_addr.sin_addr), ip, INET_ADDRSTRLEN);
                printf("Connection established with IP : %s and PORT : %d\n", ip, ntohs(proxyserver_addr.sin_port));

                recv(new_socket, message, 1024, 0);
                printf("Message from proxy server received at port: %d | %s\n", PORT, message );

                char *message = malloc(sizeof(message)+25);
                strcpy(message,"Hello from outside server");
                strcpy(buffer,message);
                free(message);
                sleep(1);

                int x  = send(new_socket, buffer, strlen(buffer),0);

        }

        close(sock);
        pthread_exit(NULL);
}


int main(){

        int iter = 0;
        int server_counter = 0;
        pthread_t thread_id[SERVERS];

        printf("Total servers: %d\n", SERVERS);
        while(iter < SERVERS)
        {
                int *arg = malloc(sizeof(*arg));
                *arg = 20101 + server_counter;

                if( pthread_create(&thread_id[iter++], 0, server_thread, arg) != 0 )
                        printf("Failed to create thread\n");

                server_counter++;
        }

        sleep(20);
        iter = 0;

        while(iter < SERVERS)
        {
                pthread_join(thread_id[iter++],NULL);
        }

        printf("DONE!\n");
        return 0;
}
