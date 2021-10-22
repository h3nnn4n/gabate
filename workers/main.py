from tasks import add


def main():
    result = add.delay(4, 4)

    print(result.get())


if __name__ == '__main__':
    main()
