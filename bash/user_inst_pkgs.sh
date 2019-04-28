grep -nwr /var/log/dpkg* -e "status installed" | awk '{print $5}' | sort | uniq
