find . -name '.git' -type d -exec echo "bash -c 'git config --global --add safe.directory ${0%/.git}'" {} \;
