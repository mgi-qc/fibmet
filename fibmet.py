import sys
import os
import csv
import glob
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-w', type=str, help='<woid>', required=True)
args = parser.parse_args()

date = datetime.datetime.now().strftime("%m%d%y")

woid_list = args.w.split(',')
outfile = f'{woid_list[0]}.prodmetrics.{date}.tsv'

if os.path.exists(outfile):
    os.remove(outfile)

samplemap_outfile = f'{woid_list[0]}.samplemap.{date}.tsv'
if os.path.exists(samplemap_outfile):
    os.remove(samplemap_outfile)
print(f'Prodmetrics outfile: {outfile}\nSamplemap outfile: {samplemap_outfile}')

header = ['External ID', 'Collection', 'PF_HQ_ALIGNED_Q20_BASES', 'Mean Insert Size', 'Contamination %',
          'WGS HET_SNP_Q', 'WGS HET_SNP_SENSITIVITY', 'Mean Coverage (Raw)']


def file_write(out_data, file_header):
    if not os.path.isfile(outfile):
        with open(outfile, 'w') as outfiletsv:
            fw = csv.DictWriter(outfiletsv, fieldnames=file_header, delimiter='\t')
            fw.writeheader()
            fw.writerow(out_data)
    else:
        with open(outfile, 'a') as outfiletsv:
            fw = csv.DictWriter(outfiletsv, fieldnames=file_header, delimiter='\t')
            fw.writerow(out_data)


for woid in woid_list:
    if not os.path.isdir(woid):
        sys.exit(f'{woid} Directory not found')

    qc_all_files = glob.glob(f'{woid}/qc.*.*/attachments/*.*.*.build38.all.tsv')

    if not glob.glob(f'{woid}/qc.*.*/attachments/*.*.*.build38.all.tsv'):
        print(f'{woid}: No QC files found')

    for infile in qc_all_files:
        results = {}
        with open(infile, 'r') as infiletsv, open(samplemap_outfile, 'a') as sm:
            fh = csv.DictReader(infiletsv, delimiter='\t')

            for line in fh:

                if 'pass' in line['STATUS']:
                    results['External ID'] = line['DNA']

                    results['Collection'] = 'NA'

                    if 'Admin Project' in line:
                        results['Collection'] = line['Admin Project']

                    if line['PF_HQ_ALIGNED_Q20_BASES']:
                        results['PF_HQ_ALIGNED_Q20_BASES'] = str(format(line['PF_HQ_ALIGNED_Q20_BASES'],
                                                                        str(len(line['PF_HQ_ALIGNED_Q20_BASES']))))
                    results['Mean Insert Size'] = line['MEAN_INSERT_SIZE']
                    if line['Freemix_Alpha']:
                        fn = '%.{}f'.format(len(line['Freemix_Alpha']))
                        results['Contamination %'] = fn % (float(line['Freemix_Alpha']) * 100)
                    results['WGS HET_SNP_Q'] = line['HET_SNP_Q']
                    results['WGS HET_SNP_SENSITIVITY'] = line['HET_SNP_SENSITIVITY']
                    results['Mean Coverage (Raw)'] = line['MEAN_COVERAGE']

                    sm.write(f'{line["DNA"]}\t{line["cram"]}\t{line["cram.md5"]}\n')
                    file_write(results, header)



