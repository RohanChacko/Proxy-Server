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
#define CLIENTS 5

void * client_thread(void *arg)
{

        int client_port = *((int *) arg);
        char message[1024];
        char buffer[1024];
        int opt = 1;
        struct sockaddr_in client_addr;
        int sock = 0, valread;
        struct sockaddr_in serv_addr;

        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
        {
                printf("\n Socket creation error \n");
                // pthread_exit(NULL);
        }

        // This is to lose the pesky "Address already in use" error message
        if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                                                      &opt, sizeof(opt))) // SOL_SOCKET is the socket layer itself
        {
            perror("setsockopt");
            exit(EXIT_FAILURE);
        }

        memset(&serv_addr, '0', sizeof(serv_addr)); // to make sure the struct is empty. Essentially sets sin_zero as 0
                                                    // which is meant to be, and rest is defined below

        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(PORT);

        // Converts an IP address in numbers-and-dots notation into either a
        // struct in_addr or a struct in6_addr depending on whether you specify AF_INET or AF_INET6.
        if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0)
        {
                printf("\nInvalid address/ Address not supported \n");
                // pthread_exit(NULL);
        }

        client_addr.sin_family = AF_INET;
        client_addr.sin_port = htons(client_port);

        // Forcefully attaching socket to the port 20100
        if (bind(sock, (struct sockaddr *)&client_addr,
                 sizeof(client_addr))<0)
        {
                perror("bind failed");
                exit(EXIT_FAILURE);
        }

        if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) // connect to the server address
        {
                printf("\nConnection Failed \n");
                // pthread_exit(NULL);
        }

        strcpy(message,"Hello from client");
        if( send(sock, message, strlen(message), 0) < 0)
        {
                printf("Send failed\n");
        }

        if(recv(sock, buffer, 1024, 0) < 0)
        {
                printf("Receive failed\n");
        }

        printf("Message received to socket %d: %s\n", client_port, buffer);

        close(sock);
        pthread_exit(NULL);
}


int main(){

        int iter = 0;
        int client_counter = 0;
        pthread_t thread_id[CLIENTS];

        printf("Total clients: %d\n", CLIENTS);
        while(iter < CLIENTS)
        {
                int *arg = malloc(sizeof(*arg));
                *arg = 25000 + client_counter;

                if( pthread_create(&thread_id[iter++], 0, client_thread, arg) != 0 )
                        printf("Failed to create thread\n");

                client_counter++;
        }

        sleep(20);
        iter = 0;

        while(iter < CLIENTS)
        {
                pthread_join(thread_id[iter++],NULL);
        }

        printf("DONE!\n");
        return 0;
}
