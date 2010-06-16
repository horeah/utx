import sys, globx


def main():
    if len(sys.argv) == 1:
        directory = '.'
        pattern = '**\*'
    else:
        sep_idx = sys.argv[1].find('\\\\')
        if sep_idx >= 0:
            directory = sys.argv[1][:sep_idx]
            pattern = sys.argv[1][sep_idx + 2:]
        else:
            directory = '.'
            pattern = sys.argv[1]
    print 'Listing "' + pattern + '" based at "' + directory + '":'

    results = globx.globxy(directory, pattern)
    for elem in results:
        print elem

if __name__ == '__main__':
    main()
