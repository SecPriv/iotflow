sleep 10
find /apps_to_analyze/ -name "*.apk" ! -name "*.split.*" -maxdepth 1 -print -exec /vsa/execute_vsa.sh {}  \;


#while true
#do
#  sleep 3
#done
