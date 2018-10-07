
# NOTE: dont print anything here

import sys

if sys.argv[1] == "proxy":
    import proxy
    proxy.main()
elif sys.argv[1] == "test":
    import test
    test.main()
elif sys.argv[1] == "cli":
    import cli
    cli.main()
else:
    import server
    server.main()

