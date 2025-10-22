import socket
import threading
import time
import csv

HOST = ''
PORT = 12345
connected_ips = set()
clients_data = {}
scores = {}

# Define updated questions and answers (Computer Networks)
single_correct_questions = [
    ("What does IP stand for?\nA. Internet Protocol\nB. Internal Process\nC. Interconnected Packet\nD. Input Protocol", "A"),
    ("Which device operates at Layer 2 of the OSI model?\nA. Router\nB. Switch\nC. Hub\nD. Modem", "B"),
    ("What is the default port number for HTTP?\nA. 80\nB. 21\nC. 23\nD. 110", "A"),
    ("Which layer is responsible for end-to-end communication?\nA. Network\nB. Transport\nC. Application\nD. Data Link", "B"),
    ("Which protocol is used to send email?\nA. FTP\nB. SMTP\nC. POP3\nD. IMAP", "B")
]

multiple_correct_questions = [
    ("Which of the following are transport layer protocols?\nA. TCP\nB. UDP\nC. IP\nD. HTTP", ["A", "B"]),
    ("Which are valid IP address classes?\nA. Class A\nB. Class B\nC. Class E\nD. Class G", ["A", "B", "C"]),
    ("Which of the following are application layer protocols?\nA. FTP\nB. DNS\nC. TCP\nD. HTTP", ["A", "B", "D"]),
    ("Which protocols use port number 443 or 80?\nA. HTTPS\nB. HTTP\nC. SSH\nD. TELNET", ["A", "B"])
]

single_word_questions = [
    ("What is the full form of DNS?", "Domain Name System"),
    ("Which device connects different networks together?", "Router")
]

marks_single = 2
marks_multiple = 4
marks_word = 3

def handle_client(conn, addr):
    ip = addr[0]
    print(f"Connection from {ip}")

    roll = conn.recv(1024).decode().strip()

    if not (roll.isdigit() and 2303101 <= int(roll) <= 2303140):
        conn.sendall("Your roll number is not authorized.".encode())
        conn.close()
        return

    if roll in scores:
        conn.sendall("Your roll number has already given answers and you cannot give now.".encode())
        conn.close()
        return

    if ip in connected_ips:
        conn.sendall("Your IP has already given answers and you cannot give now.".encode())
        conn.close()
        return

    connected_ips.add(ip)
    clients_data[ip] = {'roll': roll, 'answers': []}

    conn.sendall("You are authorized. Quiz starting now.".encode())

    score = 0

    for q, a in single_correct_questions:
        conn.sendall(q.encode())
        answer = conn.recv(1024).decode().strip().upper()
        clients_data[ip]['answers'].append(answer)
        if answer == a:
            score += marks_single

    for q, a in multiple_correct_questions:
        conn.sendall(q.encode())
        answer = conn.recv(1024).decode().strip().upper().split()
        clients_data[ip]['answers'].append(' '.join(answer))
        if sorted(answer) == sorted(a):
            score += marks_multiple

    for q, a in single_word_questions:
        conn.sendall(q.encode())
        answer = conn.recv(1024).decode().strip()
        clients_data[ip]['answers'].append(answer)
        if answer.lower() == a.lower():
            score += marks_word

    scores[roll] = score
    conn.sendall(f"Thank you. Your score: {score}".encode())
    conn.close()

def save_results():
    with open("answers.csv", "w", newline='') as f:
        writer = csv.writer(f)
        headers = ['Roll No', 'IP'] + [f"Q{i+1}" for i in range(len(single_correct_questions + multiple_correct_questions + single_word_questions))]
        writer.writerow(headers)
        for ip, data in clients_data.items():
            writer.writerow([data['roll'], ip] + data['answers'])

    with open("leaderboard.txt", "w") as f:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for roll, score in sorted_scores:
            f.write(f"{roll}: {score}\n")

    question_texts = (
        [q for q, _ in single_correct_questions] +
        [q for q, _ in multiple_correct_questions] +
        [q for q, _ in single_word_questions]
    )
    correct_answers = (
        [a for _, a in single_correct_questions] +
        [a for _, a in multiple_correct_questions] +
        [a for _, a in single_word_questions]
    )

    total_questions = len(question_texts)
    correct_counts = [0] * total_questions
    total_attempts = len(clients_data)

    for data in clients_data.values():
        answers = data['answers']
        for i, ans in enumerate(answers):
            correct = correct_answers[i]
            if isinstance(correct, list):
                given = sorted(ans.strip().split())
                if given == sorted(correct):
                    correct_counts[i] += 1
            else:
                if str(ans).strip().lower() == str(correct).strip().lower():
                    correct_counts[i] += 1

    with open("analysis.txt", "w") as f:
        for i in range(total_questions):
            f.write(f"Q{i+1}: {question_texts[i].splitlines()[0]}\n")
            f.write(f"Correct Answers: {correct_answers[i]}\n")
            f.write(f"Correct Count: {correct_counts[i]}/{total_attempts} ({(correct_counts[i]/total_attempts)*100:.2f}%)\n\n")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server started on port {PORT}")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nShutting down server and saving results...")
        save_results()
        server.close()

if __name__ == "__main__":
    main()

