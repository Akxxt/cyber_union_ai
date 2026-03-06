#!/bin/bash
# 从指定备份恢复数据库
# 用法: ./restore.sh <备份文件路径> [目标数据库路径]

if [ -z "$1" ]; then
    echo "错误: 请指定备份文件路径"
    echo "用法: $0 <备份文件路径> [目标数据库路径]"
    exit 1
fi

BACKUP_FILE=$1
DB_PATH=${2:-"/app/data/cyber_union.db"}

if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

# 如果是.gz压缩文件，先解压
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "解压备份文件..."
    gunzip -c "$BACKUP_FILE" > "${BACKUP_FILE%.gz}"
    BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

# 停止服务（建议先停止应用）
# systemctl stop cyber-union

# 恢复数据库
echo "正在恢复数据库到 $DB_PATH ..."
sqlite3 $DB_PATH ".restore '$BACKUP_FILE'"

echo "恢复完成！"