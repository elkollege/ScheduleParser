# shellcheck disable=SC2046
poetry add $(cat "../requirements.txt")
poetry add $(cat "../requirements-dev.txt") --dev

rm -rf ../dist

poetry build