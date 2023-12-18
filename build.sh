rm -rf *.so
echo "Programming language..."
command=$(ls | grep my_player)
py=$([[ $command =~ (^|[[:space:]])"my_player.py"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
py3=$([[ $command =~ (^|[[:space:]])"my_player3.py"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
cpp=$([[ $command =~ (^|[[:space:]])"my_player.cpp"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
c11=$([[ $command =~ (^|[[:space:]])"my_player11.cpp"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
java=$([[ $command =~ (^|[[:space:]])"my_player.java"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
if [ "$py" == "yes" ]; then
  cmd="python my_player.py"
  echo "PY"
elif [ "$py3" == "yes" ]; then
  cmd="python my_player3.py"
  echo "PY3"
elif [ "$cpp" == "yes" ]; then
  g++ -O2 *.cpp -o exe
  cmd="./exe"
  echo "CPP"
elif [ "$java" == "yes" ]; then
  javac my_player.java
  cmd="java my_player"
  echo "JAVA"
elif [ "$c11" == "yes" ]; then
  g++ -std=c++0x -O2 *.cpp -o exe
  cmd="./exe"
  echo "11"

else
  echo "ERROR: INVALID FILENAME"
  exit 1
fi

echo ""

#prefix="$ASNLIB/public/myplayer_play/"
prefix="./"
ta_agent=("random_player") # 1 TA players
surfix=".py"

# play funcion
# 返回值是谁赢了，也是就一play就下到决胜负
play() {
  echo Clean up... >&2
  if [ -f "input.txt" ]; then
    rm input.txt
  fi
  if [ -f "output.txt" ]; then
    rm output.txt
  fi
  cp $prefix/init/input.txt ./input.txt

  echo Start Playing... >&2

  moves=0
  # 得出谁赢了才停
  while true; do
    if [ -f "output.txt" ]; then
      rm output.txt
    fi

    echo "Black makes move..." >&2
    # $1,$2是play接收的两个参数，是运行文件的命令，可以理解为两个玩家
    # $1下一手
    eval "$1" >&2

    echo $1 >&2
    let moves+=1
    #调用host，判断胜负
    python $prefix/host.py -m $moves -v True >&2
    rst=$?

    if [[ "$rst" != "0" ]]; then
      break
    fi

    if [ -f "output.txt" ]; then
      rm output.txt
    fi

    echo "White makes move..." >&2
    # $2下棋
    eval "$2" >&2
    echo $2 >&2
    let moves+=1
    #调用host
    python $prefix/host.py -m $moves -v True >&2
    rst=$?

    if [[ "$rst" != "0" ]]; then
      break
    fi
  done

  echo $rst
}
## 下多少盘在这，交换一次先手算一盘（就是一盘要下两次）
play_time=10

### start playing ###

echo ""
echo $(date)

for i in {0..0}; do # 1 TA players
  echo ""
  echo ==Playing with ${ta_agent[i]}==
  echo $(date)
  ta_cmd="python $prefix${ta_agent[i]}$surfix"
  black_win_time=0
  white_win_time=0
  black_tie=0
  white_tie=0
  #下playtime盘
  for ((round = 1; round <= $play_time; round += 2)); do
    # TA takes Black
    echo "=====Round $round====="
    echo Black:TA White:You
    echo $ta_cmd >&2
    echo $cmd >&2
    #TA先下
    winner=$(play "$ta_cmd" "$cmd")
    if [[ "$winner" = "2" ]]; then
      echo 'White(You) win!'
      let white_win_time+=1
    elif [[ "$winner" = "0" ]]; then
      echo Tie.
      let white_tie+=1
    else
      echo 'White(You) lose.'
    fi

    # Student takes Black
    echo "=====Round $((round + 1))====="
    echo Black:You White:TA
    #我先下
    winner=$(play "$cmd" "$ta_cmd")
    if [[ "$winner" = "1" ]]; then
      echo 'Black(You) win!'
      let black_win_time+=1
    elif [[ "$winner" = "0" ]]; then
      echo Tie.
      let black_tie+=1
    else
      echo 'Black(You) lose.'
    fi
  done

  echo =====Summary=====
  echo "You play as Black Player | Win: $black_win_time | Lose: $((play_time / 2 - black_win_time - black_tie)) | Tie: $black_tie"
  echo "You play as White Player | Win: $white_win_time | Lose: $((play_time / 2 - white_win_time - black_tie)) | Tie: $white_tie"
done

#if [ -f "input.txt" ]; then
#  rm input.txt
#fi
#if [ -f "output.txt" ]; then
#    rm output.txt
#fi

if [ -e "my_player.class" ]; then
  rm *.class
fi
if [ -e "exe" ]; then
  rm exe
fi
if [ -e "__pycache__" ]; then
  rm -rf __pycache__
fi

echo ""
echo Mission Completed.
echo $(date)
#sleep 500s
