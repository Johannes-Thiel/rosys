# Installation

## On Your Computer

```bash
python3 -m pip install rosys
```

See [Getting Started](getting_started.md) for what to do next.

## On The Robot

While the above installation commands work perfectly well in local environments, on a robot it is often easier to run RoSys inside a docker container.
If you already have a `main.py` it can be as simple as running

```
docker run -it --rm -v `pwd`:/app zauberzeug/rosys
```

from the same directory.
See [Pushing Code to Robot](development.md#pushing-code-to-robot) on how to get your project onto the remote system.

More complex docker setups benefit from a compose file.
Also there are some specialties needed to start RoSys in different environments (Mac, Linux, NVidia Jetson, ...).
To simplify the usage we suggest to use a script called [`./docker.sh`](https://github.com/zauberzeug/rosys/blob/main/docker.sh) which you can also copy and adapt in your own project.
Have a look at the [project examples](https://github.com/zauberzeug/rosys/tree/main/examples) to see how a setup of your own repository may look like.