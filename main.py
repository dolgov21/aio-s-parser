import asyncio
import time
from vendor import data_parser, data_analyzer, telegram_report, database_manager
from config import load_config

config = load_config()

def main():
    rapporteur = telegram_report.Rapporteur(connection_timeout=config.parser.connection_timeout,
                                            tg_bot_token=config.tg_bot.bot_token,
                                            chat_id=config.tg_bot.admin_id)

    asyncio.run(rapporteur.send_info_message())

    start_time = time.time()
    data_scrapper = data_parser.DataScrapper(
        connection_timeout=config.parser.connection_timeout,
        max_pool_size=config.parser.max_pool_size,
        time_delta=config.parser.time_delta,
        recursion_limit=config.parser.recursion_limit
    )
    try:
        institutes_data, groups_data, students_data = asyncio.run(data_scrapper.parse_data())
    except Exception as e:
        asyncio.run(rapporteur.send_error_message())
        raise (f"data_scrapper exception"
               f"{e}")

    db_manager = database_manager.DatabaseManager(
        db_echo=config.database.db_echo,
        driver="mysql+pymysql",
        username=config.database.user,
        password=config.database.password,
        host=config.database.host,
        port=config.database.port,
        db_name=config.database.database,
        echo=True
    )
    db_manager.create_tables()
    db_manager.prepare_tables()

    db_manager.insert_data(institutes_data=institutes_data,
                           groups_data=groups_data,
                           students_data=students_data)

    tables_difference = db_manager.get_tables_difference()

    db_manager.archive_data(tables_difference['entered_students'],
                            tables_difference['left_students'])

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time}")

    analyzer = data_analyzer.DataAnalyzer()
    report_json, report_txt = analyzer.get_reports(tables_difference, elapsed_time, len(groups_data), len(students_data))

    db_manager.save_reports(report_json, report_txt)

    asyncio.run(rapporteur.send_reports(report_json=report_json,
                                        report_txt=report_txt))


if __name__ == "__main__":
    main()
#   dumping and send db!
