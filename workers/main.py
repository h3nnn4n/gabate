from tasks import add


def main():
    results = []

    for x in range(10):
        for y in range(10):
            results.append(add.delay(x, y))

    for result in results:
        print(result.get())


if __name__ == '__main__':
    main()
