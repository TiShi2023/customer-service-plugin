import time

from dingtalk import ReadSheet, WriteSheet


def read_whole_column(column: str, access_token: str, read_sheet: ReadSheet, union_id: str, workbook_id: str,
                      sheet_id: str) -> list:
    """
    读取指定列的所有数据，直到遇到空值为止
    :param column: 列名，例如 'A'
    :param access_token: 钉钉的 access_token
    :param read_sheet: ReadSheet 实例
    :param union_id: 用户的 union_id
    :param workbook_id: 工作簿的 ID
    :param sheet_id: 表格的 ID
    """
    cursor = 2
    read_flag = True
    rows = []

    while read_flag:
        time.sleep(1)
        # 读取表格数据
        resp = read_sheet.main(
            token=access_token,
            union_id=union_id,
            workbook_id=workbook_id,
            sheet_id=sheet_id,
            range_address=f'{column}{cursor}:{column}{cursor + 1000}'
        )
        values = resp['values']
        for value in values:
            if value[0] == '':
                # 结束循环
                read_flag = False
                break
            else:
                rows.append(value[0])
        cursor = cursor + 1000
    return rows


def write_row(write_range: str, values: list, token: str, write_sheet: WriteSheet, union_id: str, workbook_id: str,
              sheet_id: str):
    """
    写入一行数据到指定的范围
    :param write_range: 写入的范围，例如 'A1:B2'
    :param token: 钉钉的 access_token
    :param union_id: 用户的 union_id
    :param values: 要写入的值列表
    :param workbook_id: 工作簿的 ID
    :param sheet_id: 表格的 ID
    :param write_sheet: WriteSheet 实例
    """
    write_sheet.main(
        token=token,
        union_id=union_id,
        values=values,
        workbook_id=workbook_id,
        sheet_id=sheet_id,
        range_address=write_range
    )
