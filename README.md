## NJUPT Always in Dorm
A simple script to automatically check in for NJUPT students.

## Motivation
Beginning in 2024 Q1, NJUPT students are required to check in every night to confirm their presence in dormitory, which raises several concerns regarding student autonomy and privacy. While it is undoubtedly worth discussing the ethics of such an intrusive and paternalistic policy, the fact remains that students must comply with it.

What's worse? Due to the buggy facial recognition, students often need to check in manually even though they are in dormitory, making trouble frequently for all students.

With no hope of repealing this invasive policy, the only thing we can do is to automate the process, making it as hassle-free as possible for students.

## Usage
### Docker
#### Build from source
```bash
docker buildx build -t njupt-always-in-dorm .
docker run -d -e NJUPT_USERNAME=your_username -e NJUPT_PASSWORD=your_password njupt-always-in-dorm
```

#### Use pre-built image
```bash
docker run -d -e NJUPT_USERNAME=your_username -e NJUPT_PASSWORD=your_password ghcr.io/arcticlampyrid/njupt_always_in_dorm:latest
```

Click [here](https://github.com/ArcticLampyrid/njupt_always_in_dorm/pkgs/container/njupt_always_in_dorm) to view all available tags.

### Poetry
First, install Poetry:
```bash
# For Arch Linux users, prefer to use pacman
sudo pacman -S python-poetry
# For most users
pip install pipx
pipx ensurepath
pipx install poetry
```

Then, install this module via Poetry in a virtual environment:
```bash
poetry install
```

Finally, run it using Poetry in a virtual environment:
```bash
poetry run njupt_always_in_dorm -u your_username -p your_password
```

## Development
Development Container in VSCode is recommended for project development.

## SECURITY
If you discover any security vulnerabilities, such as credentials being sent over an unsecured network, please contact me via [Email](mailto:ArcticLampyrid@outlook.com) or [Telegram](https://t.me/alampy) and refrain from disclosing the issue publicly.

## License
Licensed under AGPL v3.0 or later. See [LICENSE](LICENSE.md) for more information.
