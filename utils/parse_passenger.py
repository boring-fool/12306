def parsePassenger(passenger_dict):
    passengers_infos_list = passenger_dict['data']['normal_passengers']
    passenger_list = []
    for passenger_info in passengers_infos_list:
        passenger_info_dict = {}
        passenger_info_dict['passenger_name'] = passenger_info.get('passenger_name', '')
        passenger_info_dict['passenger_gender'] = passenger_info.get('sex_name', '')
        passenger_info_dict['passenger_id_type_code'] = passenger_info.get('passenger_id_type_code', '')
        passenger_info_dict['passenger_id_no'] = passenger_info.get('passenger_id_no', '')
        passenger_info_dict['passenger_mobile_no'] = passenger_info.get('mobile_no', '')
        passenger_list.append(passenger_info_dict)
    return passenger_list