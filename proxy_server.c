#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/sendfile.h>
#include <errno.h>
#include <sys/time.h>
#include <pthread.h>

#define PORT 20100
#define SOCKETS 5

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
char message[1024];
char buffer[1024];


void *socket_thread(void *arg)
{

  int new_socket = *((int *)arg);
  // printf("in thread socket number: %d\n", new_socket);
  pthread_mutex_lock(&lock);
  recv(new_socket , message , 1024 , 0);
  printf("Message from client received at socket: %d | %s\n",new_socket, message );

  char *message = malloc(sizeof(message)+17);
  strcpy(message,"Hello from server");
  strcpy(buffer,message);
  free(message);
  sleep(1);

  int x  = send(new_socket,buffer,strlen(buffer),0);
  pthread_mutex_unlock(&lock);
  close(new_socket);
  pthread_exit(NULL);
}


int main(){

  int server_fd, valread, sd;
  int new_socket[SOCKETS];
  int max_sd;
  struct sockaddr_in address;  // sockaddr_in - references elements of the socket address. "in" for internet
  int opt = 1;
  int addrlen = sizeof(address);
  pthread_t thread_id[SOCKETS];
  int iter = 0;

  // Creating socket file descriptor
  if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)  // creates socket, SOCK_STREAM is for TCP. SOCK_DGRAM for UDP
  {
      perror("socket failed");
      exit(EXIT_FAILURE);
  }

  // This is to lose the pesky "Address already in use" error message
  if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                                                &opt, sizeof(opt))) // SOL_SOCKET is the socket layer itself
  {
      perror("setsockopt");
      exit(EXIT_FAILURE);
  }
  address.sin_family = AF_INET;  // Address family. For IPv6, it's AF_INET6. 29 others exist like AF_UNIX etc.
  address.sin_addr.s_addr = INADDR_ANY;  // Accept connections from any IP address - listens from all interfaces.
  address.sin_port = htons( PORT );    // Server port to open. Htons converts to Big Endian - Left to Right. RTL is Little Endian

  // Forcefully attaching socket to the port 20100
  if (bind(server_fd, (struct sockaddr *)&address,
                               sizeof(address))<0)
  {
      perror("bind failed");
      exit(EXIT_FAILURE);
  }

  // Port bind is done. You want to wait for incoming connections and handle them in some way.
  // The process is two step: first you listen(), then you accept()
  if (listen(server_fd, 3) < 0) // 3 is the maximum size of queue - connections you haven't accepted
  {
      perror("listen");
      exit(EXIT_FAILURE);
  }

  addrlen = sizeof(address);
  printf("Server capacity: %d\n", SOCKETS);
  printf("Waiting for connections ...\n");

    while(1)
    {
        if ((new_socket[iter] = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0)
        {
            perror("accept");
            exit(EXIT_FAILURE);
        }
        // printf("before thread socket: %d\n", new_socket[iter]);

        if( pthread_create(&thread_id[iter], NULL, socket_thread, &new_socket[iter]) != 0 )
        {
          printf("Failed to create thread\n");
        }

        iter++;

        if(iter >= SOCKETS)
        {
          iter = 0;

          while(iter < SOCKETS)
          {
            pthread_join(thread_id[iter++],NULL);
          }
          iter = 0;
        }
    }
  return 0;
}
