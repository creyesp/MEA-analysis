from mealib.utils import checkDirectory
from mealib.preprocessing import Sync

# exp = {'MR-0117': 0, 'MR-0118': 0, 'MR-0119': 0, 'MR-0120': 0, 'MR-0121': 0,
#        'MR-0122': 0, 'MR-0123': 0, 'MR-0124': 0, 'MR-0125': 0, 'MR-0126': 0,
#        'MR-0127': 0, 'MR-0128': 0, 'MR-0129': 0, 'MR-0130': 0, 'MR-0131': 0,
#        'MR-0133': 0, 'MR-0135': 0, 'MR-0145': 0, 'MR-0146': 0, 'MR-0147': 0,
#        'MR-0148': 0, 'MR-0149' : 0}
# exp = {'MR-0227':0,'MR-0228':1,'MR-0242':0}
# exp = {'MR-0261':2,
#         'MR-0261-2':2,
#         'MR-0262':2,
#         'MR-0263':2,
#         'MR-0263-2':2,
#         'MR-0264':2}
exp = {'000769BD54T1_263DR': 2, '000769D3C7T1_261DR': 2, '00076954F_262DR': 2}
real_fps = 59.7607
for kexp in exp:
    source_folder = '../data/raw_data/'+kexp+'/'+kexp+'_analog.mcd'
    output_folder = '../data/sync/'+kexp+'/'
    mcd_channel = exp[kexp]
    checkDirectory(output_folder)

    print('\n'+kexp)
    sync_data = Sync(kexp, real_fps)
    sync_data.read_mcd(source_folder)
    sync_data.showEntities()
    sync_data.analyzer(mcd_channel)

    sync_data.create_events()
    sync_data.add_repeated()

    sync_data.save_analyzed(output_folder)
    sync_data.save_events(output_folder)
    sync_data.close_file()
