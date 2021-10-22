import tasks


def main():
    results = []

    for i in range(5):
        results.append(tasks.a_plus_b.delay(i, i + 1))
        results.append(tasks.run_agent_task.delay())

    for result in results:
        print(result.get())


if __name__ == '__main__':
    main()
