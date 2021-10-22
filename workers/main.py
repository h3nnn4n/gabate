from tasks import run_agent


def main():
    results = []

    for i in range(5):
        results.append(run_agent.delay())

    for result in results:
        print(result.get())


if __name__ == '__main__':
    main()
