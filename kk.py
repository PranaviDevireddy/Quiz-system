import socket
import time

def interact_with_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('10.250.9.125', 12345))

    roll = input("Enter your Roll Number: ").strip()
    client.sendall(roll.encode())
    response = client.recv(1024).decode()

    # if the server sends a message saying that the roll number is not authorized or already used
    if "not authorized" in response or "already given answers" in response:
        print(response)  # print the response from the server
        client.close()  # close the connection immediately
        return  # stop execution if the roll number is invalid or already used

    print("Connected to server. You have 120 seconds to complete the quiz.\n")

    # single correct questions
    for _ in range(5):  # adjust based on your number of questions
        question = client.recv(1024).decode()
        print(question)
        answer = input("Your answer (A/B/C/D): ").strip().upper()
        client.sendall(answer.encode())

    # multiple correct questions
    for _ in range(4):  # adjust based on your number of questions
        question = client.recv(1024).decode()
        print(question)
        answer = input("Your answers (e.g. A C): ").strip().upper().split()
        client.sendall(" ".join(answer).encode())

    # single-word questions
    for _ in range(2):  # adjust based on your number of questions
        question = client.recv(1024).decode()
        print(question)
        answer = input("Your answer: ").strip()
        client.sendall(answer.encode())

    result = client.recv(1024).decode()
    print(result)
    client.close()

if __name__ == "__main__":
    interact_with_server()
