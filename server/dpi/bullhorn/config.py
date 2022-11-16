

class BullhornConfig():
    entity_types = {
        'lead' : {
            "is_contact_entity": True,
            "name": 'Lead',
            "search_query_fields": ['firstName', 'lastName', 'name', 'email', 'phone'],
            "response_fields": ['id', 'firstName', 'lastName', 'name', 'email', 'phone'],
        },
        'candidate' : {
            "is_contact_entity": True,
            "name": 'Candidate',
            "search_query_fields": ['firstName', 'lastName', 'name', 'email', 'phone'],
            "response_fields": ['id', 'firstName', 'lastName', 'name', 'email', 'phone'],
        },
        'company' : {
            "is_contact_entity": True,
            "name": 'ClientCorporation', 
            "search_query_fields": ['name',  'phone'],
            "response_fields": ['id','name',  'phone'],
        },
        'contact' : {
            "is_contact_entity": True,
            "name": 'ClientContact',
            "search_query_fields": ['firstName', 'lastName', 'name', 'email', 'phone'],
            "response_fields": ['id', 'firstName', 'lastName', 'name', 'email', 'phone'],
        },
        'note' : {
            "is_contact_entity": False,
            "name": 'Note',
            "search_query_fields": [],
            "response_fields": [],
        },
        'task' : {
            "is_contact_entity": False,
            "name": 'Task',
            "search_query_fields": [],
            "response_fields": [],
        }
    }

    rest_base_url = "https://rest91.bullhornstaffing.com/rest-services/9rsl1s/"
    get_entity_url = "search/{}"
    get_entity_by_id_url = "entity/{}/{}"
    create_entity_url = "entity/{}"
    update_entity_url = "entity/{}/{}"
    get_entity_notes_url = "entity/{}/{}/notes"
    create_task_url = ""


    free_search_fields = ['firstName', 'lastName', 'name', 'email', 'phone']
