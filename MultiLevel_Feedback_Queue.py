#Lớp tiến trình
class Process:
    def __init__(self, pid, burst_time, arrival_time=0):
        self.pid = pid
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.remaining_time = burst_time
        self.queue_level = 0
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1

#Lóp MLFQ với 2 queue round robin và 1 queue fcfs
class MultilevelFeedbackQueue:
    def __init__(self, time_quantum_list):
        self.queues = [[] for _ in range(len(time_quantum_list) + 1)]  # Thêm hàng đợi thứ 3 (FCFS)
        self.time_quantum_list = time_quantum_list
        self.current_time = 0
        self.execution_history = []

    def add_process(self, process):
        self.queues[0].append(process)

    def execute(self):
        time = 0
        completed_processes = []

        for level in range(len(self.queues)):
            while len(self.queues[level]) > 0:
                current_process = self.queues[level].pop(0)
                    
                #nếu đây là lần đầu chạy , thời gian phản hồi sẽ được điền vào
                if current_process.response_time == -1:
                    current_process.response_time = time - current_process.arrival_time

                    
                if level < len(self.time_quantum_list):  # Nếu ở hàng đợi có quantum
                    time_quantum = self.time_quantum_list[level]
                    executed_time = min(time_quantum, current_process.remaining_time)
                else:  # Hàng đợi thứ 3 sử dụng FCFS (chạy đến khi hoàn thành)
                    executed_time = current_process.remaining_time

                self.execution_history.append((time, time + executed_time, current_process.pid, level))
                    
                current_process.remaining_time -= executed_time
                time += executed_time


                if current_process.remaining_time > 0:
                    if level < len(self.queues) - 1:  # Nếu chưa đến hàng đợi cuối cùng
                        current_process.queue_level = level + 1
                        self.queues[level + 1].append(current_process)  # Đẩy xuống hàng đợi thấp hơn
                    else:
                        self.queues[level].append(current_process)  # Ở FCFS thì giữ nguyên
                else:
                    current_process.completion_time = time
                    current_process.turnaround_time = time - current_process.arrival_time
                    current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                    completed_processes.append(current_process)

        return completed_processes


def print_gantt_chart(execution_history):
    print("\nBiểu đồ Gantt:")
    max_time = max(end for _, end, _, _ in execution_history)
    
    # Vẽ đường biên trên
    print("+" + "-"*(max_time*3 + 1) + "+")
    
    # Vẽ các tiến trình
    timeline = ["  "] * (max_time + 1)
    for start, end, pid, level in execution_history:
        for t in range(start, end):
            timeline[t] = f"P{pid}"
    
    # In tiến trình
    print("|", end="")
    for t in range(max_time):
        print(f"{timeline[t]:2}", end=" ")
    print("|")
    
    # Vẽ đường biên dưới
    print("+" + "-"*(max_time*3 + 1) + "+")
    
    # In thang thời gian
    print(" ", end="")
    for t in range(max_time + 1):
        print(f"{t:2}", end=" ")
    print("\n")
    
    # In chi tiết quantum
    print("Chi tiết thực thi theo quantum:")
    print("+" + "-"*35 + "+")
    print("| Tiến trình | Quantum | Thời gian |")
    print("+" + "-"*35 + "+")
    for start, end, pid, level in execution_history:
        print(f"| P{pid:<9} | Q{level+1:<6} | {start:2} → {end:<5} |")
    print("+" + "-"*35 + "+")


def print_detailed_results(processes, quantum_list):
    print("\nBảng chi tiết kết quả thực thi với các quantum:")
    for i, q in enumerate(quantum_list):
        print(f"Q{i+1} = {q}")
        
    print("\n+" + "-"*75 + "+")
    print("| PID | Burst Time | Arrival | Completion | Turnaround | Waiting | Response |")
    print("+" + "-"*75 + "+")
    
    avg_turnaround = avg_waiting = avg_response = 0
    
    for p in sorted(processes, key=lambda x: x.pid):
        print(f"| P{p.pid:<3} | {p.burst_time:<10} | {p.arrival_time:<8} | "
              f"{p.completion_time:<10} | {p.turnaround_time:<10} | "
              f"{p.waiting_time:<7} | {p.response_time:<8} |")
        avg_turnaround += p.turnaround_time
        avg_waiting += p.waiting_time
        avg_response += p.response_time
        
    print("+" + "-"*75 + "+")
    n = len(processes)
    print(f"\nThời gian hoàn thành trung bình: {avg_turnaround/n:.2f}")
    print(f"Thời gian chờ trung bình: {avg_waiting/n:.2f}")
    print(f"Thời gian phản hồi trung bình: {avg_response/n:.2f}")


if __name__ == "__main__":
    # Khởi tạo các tiến trình
    processes = [
        Process(1, 10, 0),  # P1: burst=10, arrival=0
        Process(2, 6, 0),   # P2: burst=6, arrival=0
        Process(3, 8, 0),   # P3: burst=8, arrival=0
        Process(4, 4, 0)    # P4: burst=4, arrival=0
    ]
    
    # Khởi tạo MLFQ với Q1=4, Q2=8
    time_quantum_list = [4, 8]
    mlfq = MultilevelFeedbackQueue(time_quantum_list)
    
    # Thêm tiến trình vào hàng đợi
    for process in processes:
        mlfq.add_process(process)
    
    # Thực thi và lấy kết quả
    completed_processes = mlfq.execute()
    
    # Hiển thị kết quả
    print_detailed_results(completed_processes, time_quantum_list)
    print_gantt_chart(mlfq.execution_history)