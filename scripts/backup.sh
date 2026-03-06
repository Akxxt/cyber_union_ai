#!/bin/bash
# SQLite数据库备份脚本
# 用法: ./backup.sh [备份目录]

BACKUP_DIR=${1:-"/var/backups/cyber_union"}
DB_PATH=${2:-"/app/data/cyber_union.db"}
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 执行备份
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/cyber_union_$DATE.db'"

# 压缩备份（可选）
gzip -f $BACKUP_DIR/cyber_union_$DATE.db

# 保留最近7天的备份，清理旧备份
find $BACKUP_DIR -name "cyber_union_*.db.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_DIR/cyber_union_$DATE.db.gz"