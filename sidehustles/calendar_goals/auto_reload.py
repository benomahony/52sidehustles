from watchfiles import run_process


def rebuild():
    import subprocess

    subprocess.run(["python", "sidehustles/calendar_goals/main.py"])
    print("Reloading pdf")


if __name__ == "__main__":
    run_process("sidehustles/calendar_goals/main.py", target=rebuild)
