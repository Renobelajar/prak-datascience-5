NAMA = "Reno Miftahudin"
NIM = "NIM Kamu"

proses = {
    "P1": {"burst": 22, "priority": 1},
    "P2": {"burst": 15, "priority": 4},
    "P3": {"burst": 5, "priority": 2},
    "P4": {"burst": 14, "priority": 3},
    "P5": {"burst": 5, "priority": 5},
    "P6": {"burst": 7, "priority": 6}
}

QUANTUM = 6


def tampilkan_hasil(nama_algoritma, gantt, burst):
    selesai = {}

    print("\n" + "=" * 55)
    print(nama_algoritma)
    print("=" * 55)
    print("Nama:", NAMA)
    print("NIM:", NIM)

    print("\nGantt Chart:")
    print(" | ".join(
        f"{p} ({mulai}-{akhir})"
        for p, mulai, akhir in gantt
    ))

    for p, mulai, akhir in gantt:
        selesai[p] = akhir

    print("\nProses\tBT\tCT\tWT")
    total_wt = 0

    for p in burst:
        bt = burst[p]
        ct = selesai[p]
        wt = ct - bt
        total_wt += wt

        print(f"{p}\t{bt}\t{ct}\t{wt}")

    awt = total_wt / len(burst)

    print("Total Waiting Time =", total_wt)
    print(f"Average Waiting Time = {awt:.2f}")


def fcfs(burst):
    gantt = []
    waktu = 0

    for p, bt in burst.items():
        mulai = waktu
        waktu += bt
        gantt.append((p, mulai, waktu))

    tampilkan_hasil("A. FCFS", gantt, burst)


def sjf(burst):
    urutan = sorted(burst, key=lambda p: burst[p])
    gantt = []
    waktu = 0

    for p in urutan:
        mulai = waktu
        waktu += burst[p]
        gantt.append((p, mulai, waktu))

    tampilkan_hasil("B. SJF", gantt, burst)


def round_robin(burst, quantum):
    sisa = burst.copy()
    waktu = 0
    gantt = []
    antrean = list(burst.keys())

    while antrean:
        p = antrean.pop(0)
        mulai = waktu
        durasi = min(quantum, sisa[p])

        waktu += durasi
        sisa[p] -= durasi
        gantt.append((p, mulai, waktu))

        if sisa[p] > 0:
            antrean.append(p)

    tampilkan_hasil("C. Round Robin", gantt, burst)


def priority_scheduling(data):
    urutan = sorted(
        data,
        key=lambda p: data[p]["priority"]
    )

    burst = {
        p: data[p]["burst"] for p in data
    }

    gantt = []
    waktu = 0

    for p in urutan:
        mulai = waktu
        waktu += burst[p]
        gantt.append((p, mulai, waktu))

    tampilkan_hasil(
        "D. Priority Scheduling",
        gantt,
        burst
    )


burst_time = {
    p: data["burst"] for p, data in proses.items()
}

fcfs(burst_time)
sjf(burst_time)
round_robin(burst_time, QUANTUM)
priority_scheduling(proses)
