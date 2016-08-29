import csv


def seperate_Http_Https():
    csv_input_file = 'Labeled-http-50.csv'
    csv_http_out = 'only-http-50.csv'
    csv_https_out = 'only-httpssl-50.csv'

    with open(csv_input_file, mode='r', newline='') as csv_input_file:
        row_content_rdr = csv.reader(csv_input_file, delimiter=',')
        with open(csv_http_out, mode='w', newline='') as csv_http_file:
            with open(csv_https_out, mode='w', newline='') as csv_https_file:
                for single_row in row_content_rdr:
                    if single_row[1] == 'http':
                        http_writer = csv.writer(csv_http_file, delimiter=',')
                        http_writer.writerow([single_row[0], single_row[1]])
                    elif single_row[1] == 'https':
                        https_writer = csv.writer(csv_https_file, delimiter=',')
                        https_writer.writerow([single_row[0], single_row[1]])


seperate_Http_Https()

# def read_csv_file():
#     csv_filepath = self.csvInputFilePath
#     with open(csv_filepath, mode='r', newline='') as csvfile:
#         domain_name_rdr = csv.reader(csvfile, delimiter=',')
#         for row in domain_name_rdr:
#             self.all_domains.append(row[1])
#
#
# def write_csv_file():
#     csv_out = self.csvOutputPath
#     tempfile = NamedTemporaryFile(delete=False)
#     self.logger.debug("Domain: [%s] | Proto: [%s] | Loc-Proto: [%s]" % (
#     self.all_row_data[0][0], self.all_row_data[0][1], self.all_row_data[0][2]))
#     self.logger.debug("Domain: [%s] | Proto: [%s] | Loc-Proto: [%s]" % (
#     self.all_row_data[1][0], self.all_row_data[1][1], self.all_row_data[1][2]))
#     with open(csv_out, mode='w', newline='') as tempfile:
#         writer = csv.writer(tempfile, delimiter=',')
#
#         for row in self.all_row_data:
#             # writer.writerow([row.item])
#             self.logger.debug("Domain: [%s] | Proto: [%s] | Loc-Proto: [%s]" % (row[0], row[1], row[2]))
#             # writer.writerow([row[0],row[1],row[2]])    # 3 rows with Domain, Initial-HTTP[S], Location HTTP[S]
#             if row[1] == 'https' or row[2] == 'https':  # 2 rows with Domain HTTP or HTTPS (Final location)
#                 writer.writerow([row[0], 'https'])
#             elif row[1] == 'Timeout' or row[2] == 'Timeout':
#                 writer.writerow([row[0], 'Timeout'])
#             else:
#                 writer.writerow([row[0], 'http'])
