from rsnapshot_docker_compose_backup import docker
from tests.unit.docker_api_util import mock_responses
from typing import Any, Dict

ubuntu_container: Dict[str, Any] = {
    "default_ps": {
        "Id": "8dfafdbc3a40",
        "Names": ["/boring_feynman"],
        "Image": "ubuntu:latest",
        "ImageID": "d74508fb6632491cea586a1fd7d748dfc5274cd6fdfedee309ecdcbc2bf5cb82",
        "Command": "echo 1",
        "Created": 1367854155,
        "State": "Exited",
        "Status": "Exit 0",
        "Ports": [{"PrivatePort": 2222, "PublicPort": 3333, "Type": "tcp"}],
        "Labels": {
            "com.example.vendor": "Acme",
            "com.example.license": "GPL",
            "com.example.version": "1.0",
        },
        "SizeRw": 12288,
        "SizeRootFs": 0,
        "HostConfig": {
            "NetworkMode": "default",
            "Annotations": {"io.kubernetes.docker.type": "container"},
        },
        "NetworkSettings": {
            "Networks": {
                "bridge": {
                    "NetworkID": "7ea29fc1412292a2d7bba362f9253545fecdfa8ce9a6e37dd10ba8bee7129812",
                    "EndpointID": "2cdc4edb1ded3631c81f57966563e5c8525b81121bb3706a9a9a3ae102711f3f",
                    "Gateway": "172.17.0.1",
                    "IPAddress": "172.17.0.2",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:ac:11:00:02",
                }
            }
        },
        "Mounts": [
            {
                "Name": "fac362...80535",
                "Source": "/data",
                "Destination": "/data",
                "Driver": "local",
                "Mode": "ro,Z",
                "RW": False,
                "Propagation": "",
            }
        ],
    },
}

postgres_container: Dict[str, Any] = {
    "compose_ps": {
        "Id": "5bd36e44a3b8a955821594e440aeac530b84e3f19e262b240c5b6ccc123a9efb",
        "Names": ["/postgres-postgres-1"],
        "Image": "postgres",
        "ImageID": "sha256:f23dc7cd74bd7693fc164fd829b9a7fa1edf8eaaed488c117312aef2a48cafaa",
        "Command": "docker-entrypoint.sh postgres",
        "Created": 1720380887,
        "Ports": [{"PrivatePort": 5432, "Type": "tcp"}],
        "Labels": {
            "com.docker.compose.config-hash": "9a117cd07c5e5084a9f556772048160a3ec8b6cf5ef854259394d9b4534d9493",
            "com.docker.compose.container-number": "1",
            "com.docker.compose.depends_on": "",
            "com.docker.compose.image": "sha256:f23dc7cd74bd7693fc164fd829b9a7fa1edf8eaaed488c117312aef2a48cafaa",
            "com.docker.compose.oneoff": "False",
            "com.docker.compose.project": "postgres",
            "com.docker.compose.project.config_files": "/tmp/compose/postgres/docker-compose.yml",
            "com.docker.compose.project.working_dir": "/tmp/compose/postgres",
            "com.docker.compose.replace": "13d3c254654a3b9c8952d9b720e1b626c34067519c242bbea4dab8e27df52349",
            "com.docker.compose.service": "postgres",
            "com.docker.compose.version": "2.28.1",
        },
        "State": "running",
        "Status": "Up 22 seconds",
        "HostConfig": {"NetworkMode": "postgres_default"},
        "NetworkSettings": {
            "Networks": {
                "postgres_default": {
                    "IPAMConfig": None,
                    "Links": None,
                    "Aliases": None,
                    "MacAddress": "02:42:ac:15:00:02",
                    "DriverOpts": None,
                    "NetworkID": "8709e87e492101ced27005fca500d8de01e53ef7f4d17e2991fe87b68df70a1c",
                    "EndpointID": "56a2ec22f6c3031f990370f822a6e8ef0853301e40204e9b2a9acdcc35f99868",
                    "Gateway": "172.21.0.1",
                    "IPAddress": "172.21.0.2",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "DNSNames": None,
                }
            }
        },
        "Mounts": [
            {
                "Type": "volume",
                "Name": "f7cee7429e858fd5bcbdf496e1e3d75ffe01b01592d6e2c804c784f26d8a564f",
                "Source": "/var/lib/docker/volumes/f7cee7429e858fd5bcbdf496e1e3d75ffe01b01592d6e2c804c784f26d8a564f/_data",
                "Destination": "/var/lib/postgresql/data",
                "Driver": "local",
                "Mode": "z",
                "RW": True,
                "Propagation": "",
            }
        ],
    },
    "compose_inspect": {
        "Id": "5bd36e44a3b8a955821594e440aeac530b84e3f19e262b240c5b6ccc123a9efb",
        "Created": "2024-07-07T19:34:47.268750145Z",
        "Path": "docker-entrypoint.sh",
        "Args": ["postgres"],
        "State": {
            "Status": "running",
            "Running": True,
            "Paused": False,
            "Restarting": False,
            "OOMKilled": False,
            "Dead": False,
            "Pid": 30997,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2024-07-07T19:37:16.277868701Z",
            "FinishedAt": "2024-07-07T19:37:13.655314385Z",
        },
        "Image": "sha256:f23dc7cd74bd7693fc164fd829b9a7fa1edf8eaaed488c117312aef2a48cafaa",
        "ResolvConfPath": "/var/lib/docker/containers/5bd36e44a3b8a955821594e440aeac530b84e3f19e262b240c5b6ccc123a9efb/resolv.conf",
        "HostnamePath": "/var/lib/docker/containers/5bd36e44a3b8a955821594e440aeac530b84e3f19e262b240c5b6ccc123a9efb/hostname",
        "HostsPath": "/var/lib/docker/containers/5bd36e44a3b8a955821594e440aeac530b84e3f19e262b240c5b6ccc123a9efb/hosts",
        "LogPath": "/var/lib/docker/containers/5bd36e44a3b8a955821594e440aeac530b84e3f19e262b240c5b6ccc123a9efb/5bd36e44a3b8a955821594e440aeac530b84e3f19e262b240c5b6ccc123a9efb-json.log",
        "Name": "/postgres-postgres-1",
        "RestartCount": 0,
        "Driver": "overlay2",
        "Platform": "linux",
        "MountLabel": "",
        "ProcessLabel": "",
        "AppArmorProfile": "docker-default",
        "ExecIDs": None,
        "HostConfig": {
            "Binds": None,
            "ContainerIDFile": "",
            "LogConfig": {"Type": "json-file", "Config": {}},
            "NetworkMode": "postgres_default",
            "PortBindings": {},
            "RestartPolicy": {"Name": "no", "MaximumRetryCount": 0},
            "AutoRemove": False,
            "VolumeDriver": "",
            "VolumesFrom": None,
            "ConsoleSize": [0, 0],
            "CapAdd": None,
            "CapDrop": None,
            "CgroupnsMode": "private",
            "Dns": None,
            "DnsOptions": None,
            "DnsSearch": None,
            "ExtraHosts": [],
            "GroupAdd": None,
            "IpcMode": "private",
            "Cgroup": "",
            "Links": None,
            "OomScoreAdj": 0,
            "PidMode": "",
            "Privileged": False,
            "PublishAllPorts": False,
            "ReadonlyRootfs": False,
            "SecurityOpt": None,
            "UTSMode": "",
            "UsernsMode": "",
            "ShmSize": 67108864,
            "Runtime": "runc",
            "Isolation": "",
            "CpuShares": 0,
            "Memory": 0,
            "NanoCpus": 0,
            "CgroupParent": "",
            "BlkioWeight": 0,
            "BlkioWeightDevice": None,
            "BlkioDeviceReadBps": None,
            "BlkioDeviceWriteBps": None,
            "BlkioDeviceReadIOps": None,
            "BlkioDeviceWriteIOps": None,
            "CpuPeriod": 0,
            "CpuQuota": 0,
            "CpuRealtimePeriod": 0,
            "CpuRealtimeRuntime": 0,
            "CpusetCpus": "",
            "CpusetMems": "",
            "Devices": None,
            "DeviceCgroupRules": None,
            "DeviceRequests": None,
            "MemoryReservation": 0,
            "MemorySwap": 0,
            "MemorySwappiness": None,
            "OomKillDisable": None,
            "PidsLimit": None,
            "Ulimits": None,
            "CpuCount": 0,
            "CpuPercent": 0,
            "IOMaximumIOps": 0,
            "IOMaximumBandwidth": 0,
            "Mounts": [
                {
                    "Type": "volume",
                    "Source": "f7cee7429e858fd5bcbdf496e1e3d75ffe01b01592d6e2c804c784f26d8a564f",
                    "Target": "/var/lib/postgresql/data",
                }
            ],
            "MaskedPaths": [
                "/proc/asound",
                "/proc/acpi",
                "/proc/kcore",
                "/proc/keys",
                "/proc/latency_stats",
                "/proc/timer_list",
                "/proc/timer_stats",
                "/proc/sched_debug",
                "/proc/scsi",
                "/sys/firmware",
                "/sys/devices/virtual/powercap",
            ],
            "ReadonlyPaths": [
                "/proc/bus",
                "/proc/fs",
                "/proc/irq",
                "/proc/sys",
                "/proc/sysrq-trigger",
            ],
        },
        "GraphDriver": {
            "Data": {
                "LowerDir": "/var/lib/docker/overlay2/c8c3414cf886863da57cb3c984f96a14bcf2593141a7ff0551c2600e26607e4d-init/diff:/var/lib/docker/overlay2/2994337a61dc305434718d25bde49c883194da86eff279c11621d73204767a59/diff:/var/lib/docker/overlay2/ee965a886ad5c5e59e4a8146ed14d832cab48196e5a0b2e0086c85bc06c90afe/diff:/var/lib/docker/overlay2/f41cf7ffdc09cc6cf9fdbbfdd815c5164b70948a983c772cc3d6c26887466259/diff:/var/lib/docker/overlay2/4350ba79736ec08948f7da77de1dcb99b96ddfeb3668944935316df2f7aa7839/diff:/var/lib/docker/overlay2/54db96cc90846f5051bed7ad7ea747256ae5941fc62b424a12f33835e09e271f/diff:/var/lib/docker/overlay2/ebb730254e34df20e4be01084977f24b4414e1f40365ecbf37d7880b09fd1d4f/diff:/var/lib/docker/overlay2/c6d09f8e64cab0b58e13f23894e97d086401726f274e931a7c2bf2f17b59eefa/diff:/var/lib/docker/overlay2/d9a7801c63a9152227b5a74d88500dd81cf90d57bb94e498ec8b5ed80ba9c2f6/diff:/var/lib/docker/overlay2/e5747377d64838623fb718566094b79f1fbb55ee2938d7095f765db159511f5f/diff:/var/lib/docker/overlay2/328676f04e1005fa62045241a0deb1f117021f7d445a98360674d20fca4dab84/diff:/var/lib/docker/overlay2/37aa59a21db6a80bbdf6528621576b35bb3f2fa34ec42077f92c91652fe80a70/diff:/var/lib/docker/overlay2/91e31c15491e84aec0733126fd2f4c55ee25aba4d2ad1c952bbb5d4dcc446a67/diff:/var/lib/docker/overlay2/d37eb661f7892c9b86772a26c0481a2cc4eeda70fb37c8b2bb4f862c8b1bfc59/diff:/var/lib/docker/overlay2/a9de29b7974fb1b8d62b3a888f1b0e35eb52f5961c4bba57ccca017dbb44deb7/diff",
                "MergedDir": "/var/lib/docker/overlay2/c8c3414cf886863da57cb3c984f96a14bcf2593141a7ff0551c2600e26607e4d/merged",
                "UpperDir": "/var/lib/docker/overlay2/c8c3414cf886863da57cb3c984f96a14bcf2593141a7ff0551c2600e26607e4d/diff",
                "WorkDir": "/var/lib/docker/overlay2/c8c3414cf886863da57cb3c984f96a14bcf2593141a7ff0551c2600e26607e4d/work",
            },
            "Name": "overlay2",
        },
        "Mounts": [
            {
                "Type": "volume",
                "Name": "f7cee7429e858fd5bcbdf496e1e3d75ffe01b01592d6e2c804c784f26d8a564f",
                "Source": "/var/lib/docker/volumes/f7cee7429e858fd5bcbdf496e1e3d75ffe01b01592d6e2c804c784f26d8a564f/_data",
                "Destination": "/var/lib/postgresql/data",
                "Driver": "local",
                "Mode": "z",
                "RW": True,
                "Propagation": "",
            }
        ],
        "Config": {
            "Hostname": "5bd36e44a3b8",
            "Domainname": "",
            "User": "",
            "AttachStdin": False,
            "AttachStdout": True,
            "AttachStderr": True,
            "ExposedPorts": {"5432/tcp": {}},
            "Tty": False,
            "OpenStdin": False,
            "StdinOnce": False,
            "Env": [
                "POSTGRES_HOST_AUTH_METHOD=trust",
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/postgresql/16/bin",
                "GOSU_VERSION=1.17",
                "LANG=en_US.utf8",
                "PG_MAJOR=16",
                "PG_VERSION=16.3-1.pgdg120+1",
                "PGDATA=/var/lib/postgresql/data",
            ],
            "Cmd": ["postgres"],
            "Image": "postgres",
            "Volumes": {"/var/lib/postgresql/data": {}},
            "WorkingDir": "",
            "Entrypoint": ["docker-entrypoint.sh"],
            "OnBuild": None,
            "Labels": {
                "com.docker.compose.config-hash": "9a117cd07c5e5084a9f556772048160a3ec8b6cf5ef854259394d9b4534d9493",
                "com.docker.compose.container-number": "1",
                "com.docker.compose.depends_on": "",
                "com.docker.compose.image": "sha256:f23dc7cd74bd7693fc164fd829b9a7fa1edf8eaaed488c117312aef2a48cafaa",
                "com.docker.compose.oneoff": "False",
                "com.docker.compose.project": "postgres",
                "com.docker.compose.project.config_files": "/tmp/compose/postgres/docker-compose.yml",
                "com.docker.compose.project.working_dir": "/tmp/compose/postgres",
                "com.docker.compose.replace": "13d3c254654a3b9c8952d9b720e1b626c34067519c242bbea4dab8e27df52349",
                "com.docker.compose.service": "postgres",
                "com.docker.compose.version": "2.28.1",
            },
            "StopSignal": "SIGINT",
        },
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "c3533bcc7c20b7b1c4f9ac871655e4775f4db4157744bf51b23126b3fe6b55a9",
            "SandboxKey": "/var/run/docker/netns/c3533bcc7c20",
            "Ports": {"5432/tcp": None},
            "HairpinMode": False,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "SecondaryIPAddresses": None,
            "SecondaryIPv6Addresses": None,
            "EndpointID": "",
            "Gateway": "",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "IPAddress": "",
            "IPPrefixLen": 0,
            "IPv6Gateway": "",
            "MacAddress": "",
            "Networks": {
                "postgres_default": {
                    "IPAMConfig": None,
                    "Links": None,
                    "Aliases": ["postgres-postgres-1", "postgres"],
                    "MacAddress": "02:42:ac:15:00:02",
                    "DriverOpts": None,
                    "NetworkID": "8709e87e492101ced27005fca500d8de01e53ef7f4d17e2991fe87b68df70a1c",
                    "EndpointID": "56a2ec22f6c3031f990370f822a6e8ef0853301e40204e9b2a9acdcc35f99868",
                    "Gateway": "172.21.0.1",
                    "IPAddress": "172.21.0.2",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "DNSNames": ["postgres-postgres-1", "postgres", "5bd36e44a3b8"],
                }
            },
        },
    },
}

mariadb_container: Dict[str, Any] = {
    "compose_ps": {
        "Id": "38bc5ec7316e3722e4cfe632add2c92906f2ca86a8ed2bf6e1d65d7356a0a3f2",
        "Names": ["/mariadb-maraidb-1"],
        "Image": "mariadb",
        "ImageID": "sha256:4486d64c9c3b538b6dee6bcd5ea0ac5f74ea5e3cafc71181a54ec678ae0370aa",
        "Command": "docker-entrypoint.sh mariadbd",
        "Created": 1720384955,
        "Ports": [{"PrivatePort": 3306, "Type": "tcp"}],
        "Labels": {
            "com.docker.compose.config-hash": "cc177b7cde84d71b09914c04791d6b9468def23e6542a350865396737cb95d21",
            "com.docker.compose.container-number": "1",
            "com.docker.compose.depends_on": "",
            "com.docker.compose.image": "sha256:4486d64c9c3b538b6dee6bcd5ea0ac5f74ea5e3cafc71181a54ec678ae0370aa",
            "com.docker.compose.oneoff": "False",
            "com.docker.compose.project": "mariadb",
            "com.docker.compose.project.config_files": "/tmp/compose/mariadb/docker-compose.yml",
            "com.docker.compose.project.working_dir": "/tmp/compose/mariadb",
            "com.docker.compose.replace": "47a517268708567174b09a5f057e079926ee5772bb130542ed07fc889914e773",
            "com.docker.compose.service": "maraidb",
            "com.docker.compose.version": "2.28.1",
            "org.opencontainers.image.authors": "MariaDB Community",
            "org.opencontainers.image.base.name": "docker.io/library/ubuntu:noble",
            "org.opencontainers.image.description": "MariaDB Database for relational SQL",
            "org.opencontainers.image.documentation": "https://hub.docker.com/_/mariadb/",
            "org.opencontainers.image.licenses": "GPL-2.0",
            "org.opencontainers.image.ref.name": "ubuntu",
            "org.opencontainers.image.source": "https://github.com/MariaDB/mariadb-docker",
            "org.opencontainers.image.title": "MariaDB Database",
            "org.opencontainers.image.url": "https://github.com/MariaDB/mariadb-docker",
            "org.opencontainers.image.vendor": "MariaDB Community",
            "org.opencontainers.image.version": "11.4.2",
        },
        "State": "running",
        "Status": "Up 39 seconds",
        "HostConfig": {"NetworkMode": "mariadb_default"},
        "NetworkSettings": {
            "Networks": {
                "mariadb_default": {
                    "IPAMConfig": None,
                    "Links": None,
                    "Aliases": None,
                    "MacAddress": "02:42:ac:15:00:02",
                    "DriverOpts": None,
                    "NetworkID": "6028c4b4d1f352e835f3f2c8100109d7b38f46208efbe74be743ce03ce5a672d",
                    "EndpointID": "c44b7c8af24e3001ff2f0bc978ef13f05327a24bd74ce6792837c2be5df256e0",
                    "Gateway": "172.21.0.1",
                    "IPAddress": "172.21.0.2",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "DNSNames": None,
                }
            }
        },
        "Mounts": [
            {
                "Type": "volume",
                "Name": "7122382a6fa637a5a0c5430e11bc2825b8c7bb7a1afdc12f2f6fb080c0ca14c6",
                "Source": "/var/lib/docker/volumes/7122382a6fa637a5a0c5430e11bc2825b8c7bb7a1afdc12f2f6fb080c0ca14c6/_data",
                "Destination": "/var/lib/mysql",
                "Driver": "local",
                "Mode": "z",
                "RW": True,
                "Propagation": "",
            }
        ],
    }
}


def test_get_container() -> None:
    mock_responses(
        [
            (
                200,
                [
                    ubuntu_container["default_ps"],
                    postgres_container["compose_ps"],
                ],
            )
        ]
    )
    response = docker.get_container(socket_connection="http://localhost:8000")
    assert response[1].image == "postgres"
    assert response[0].id.startswith("8dfafdbc3a40")


def test_inspect_container() -> None:
    mock_responses(
        [
            (
                200,
                postgres_container["compose_inspect"],
            )
        ]
    )
    response = docker.inspect_container(
        "5bd36e44a3b8", socket_connection="http://localhost:8000"
    )
    assert response.image == "postgres"
    assert response.id.startswith("5bd36e44a3b8")


def test_get_compose_container() -> None:
    mock_responses(
        [
            (
                200,
                [
                    postgres_container["compose_ps"],
                    mariadb_container["compose_ps"],
                    ubuntu_container["default_ps"],
                ],
            )
        ]
    )
    response = docker.get_compose_container(socket_connection="http://localhost:8000")
    assert len(response) == 2
    assert response[0].project_name == "mariadb"
    assert response[1].project_name == "postgres"


def test_get_compose_container_fixed_order() -> None:
    mock_responses(
        [
            (
                200,
                [
                    postgres_container["compose_ps"],
                    mariadb_container["compose_ps"],
                    ubuntu_container["default_ps"],
                ],
            ),
            (
                200,
                [
                    mariadb_container["compose_ps"],
                    ubuntu_container["default_ps"],
                    postgres_container["compose_ps"],
                ],
            ),
        ]
    )
    response1 = docker.get_compose_container(socket_connection="http://localhost:8000")
    response2 = docker.get_compose_container(socket_connection="http://localhost:8000")
    assert response1 == response2
