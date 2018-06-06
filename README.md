### WARNING: IN PROGRESS, DO NOT USE

### Avalon on Docker

Avalon on Docker, ideal for beginners and studios alike.

> NOTE: This currently *only* works on [Docker Toolbox](https://github.com/docker/toolbox#installation-and-documentation), *not* Docker for Windows

<br>

### Usage on Windows

With Docker available on your system, run the following commands to start Avalon and expose resources on `A:\`.

```bash
$ docker run --rm -p 445:445 -p 27017:27017 getavalon/docker:0.2
```

<details>
 <summary>Trouble?</summary>
  <br>
  <ul>
    <li>On Windows and OSX, find your IP via <code>docker-machine ip</code></li>
    <li>On Linux, exclude mapping of ports to the host and access the container IP directly</li>
  </ul>
</details>

<br>

Next, from `cmd.exe` run the following to map Avalon files to a drive, such as `A:\`

```bash
$ net use /delete a:
$ net use a: \\192.168.99.100\avalon /user:avalon default
```

<details>
 <summary>Trouble?</summary>
  <br>
  <ul>
    <li>If you encounter <code>The network name cannot be found</code> ensure you run the above in <code>cmd.exe</code> and not <code>Docker Quickstart, bash</code> or <code>MSYS2</code> etc.</li>
  </ul>
</details>

<br>

### Development

This repository contains all of Avalon as Git submodules. To extend Avalon, you typically edit each repository individually, and then point the submodules in this repository to your latest change.

```bash
$ git clone https://github.com/getavalon/docker.git --recursive
$ cd docker
$ docker build . -t getavalon/docker
$ docker run -ti --rm -p 27017:27017 -p 445:445 -p 139:139 getavalon/docker
```

Once the Docker container is running, you now have a Mongo database running. This means you can modify the code in the ```docker``` repository without restart or rebuilding the container.
