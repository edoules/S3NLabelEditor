import os

from lib_s3py.sys3 import analyze

if __name__ == "__main__":
    """
    root = 'examples'
    examples = [os.path.join(root, _ls_) for _ls_ in os.listdir(root) if _ls_.split('.')[-1] == 'abi']
    for eg in examples:
        with open(eg) as h:
            analyze(h)
    """

    import sys

    if len(sys.argv) < 2:
        exit("USAGE: [abi_file_to_analyze]")
    
    with open(sys.argv[1]) as h:
        outstr = analyze(h)
        print outstr
