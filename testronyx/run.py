from agent import TestronyxAgent
from ioc import ioc

def main():
    agent = ioc.get(TestronyxAgent)
    agent.start()
    # TODO: remove while loop
    while(True):
        pass

if __name__ == '__main__':
    main()