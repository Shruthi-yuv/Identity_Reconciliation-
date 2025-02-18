# from django.shortcuts import render

# # Create your views here.
# from django.http import JsonResponse
# from .models import Contact
# from django.views.decorators.csrf import csrf_exempt
# import json
# from django.db import transaction

# @csrf_exempt
# def identify(request):
#     if request.method == 'POST':
#         try:
#             # Parse the incoming JSON data
#             data = json.loads(request.body)

#             # Extract email and phone number from the request
#             email = data.get('email')
#             phone_number = str(data.get('phoneNumber')) if data.get('phoneNumber') else None

#             # Find existing contact based on email or phone number
#             if email:
#                 contact = Contact.objects.filter(email=email).first()
#             if phone_number:
#                  phone_contact = Contact.objects.filter(phoneNumber=phone_number).first()
#                  if phone_contact:
#                     contact = phone_contact
#                 # if contact:
#                 #     contact = Contact.objects.filter(phoneNumber=phone_number).first()
#                 # else:
#                 #     contact = Contact.objects.filter(phoneNumber=phone_number).first()

#             # If no contact is found, create a new one
#             if not contact:
#                 new_contact = Contact.objects.create(
#                     email=email,
#                     phoneNumber=phone_number,
#                     linkPrecedence='primary'
#                 )
#                 return JsonResponse({
#                     "contact": {
#                         "primaryContatctId": new_contact.id,
#                         "emails": [new_contact.email] if new_contact.email else [],
#                         "phoneNumbers": [new_contact.phoneNumber] if new_contact.phoneNumber else [],
#                         "secondaryContactIds": []
#                     }
#                 })

#             # If a contact is found, check if it's a secondary contact
#             # primary_contact = None
#             # if contact.linkedId is None:  # Primary contact
#             #     primary_contact = contact
#             # else:
#             #     primary_contact = contact.linkedId  # Follow the linkedId to get the primary contact

#             primary_contact = contact
#             if contact.linkedId:  # If contact is secondary, get primary
#                 primary_contact = contact.linkedId

#             # Get all secondary contacts for the primary contact
#             # secondary_contacts = Contact.objects.filter(linkedId=primary_contact).exclude(id=primary_contact.id)
#             secondary_contacts = Contact.objects.filter(linkedId=primary_contact)

#             # Prepare the response
#             response_data = {
#                 "contact": {
#                     "primaryContatctId": primary_contact.id,
#                     "emails": list(set([primary_contact.email] + [c.email for c in secondary_contacts if c.email])),
#                     "phoneNumbers": list(set([primary_contact.phoneNumber] + [c.phoneNumber for c in secondary_contacts if c.phoneNumber])),
#                     "secondaryContactIds": [c.id for c in secondary_contacts]
#                 }
#             }
            
#             return JsonResponse(response_data)

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
        

#     elif request.method == 'GET':
#         # Handle GET request to return all contacts (for viewing/debugging purposes)
#         try:
#             contacts = Contact.objects.all()
#             contacts_data = []
#             for contact in contacts:
#                 contacts_data.append({
#                     "id": contact.id,
#                     "email": contact.email,
#                     "phoneNumber": contact.phoneNumber,
#                     "linkedId": contact.linkedId.id if contact.linkedId else None,
#                     "linkPrecedence": contact.linkPrecedence,
#                     "createdAt": contact.createdAt,
#                     "updatedAt": contact.updatedAt,
#                     "deletedAt": contact.deletedAt,
#                 })

#             return JsonResponse({"contacts": contacts_data}, safe=False)

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
    

#     return JsonResponse({"error": "Invalid method"}, status=405)



from django.shortcuts import render
from django.http import JsonResponse
from .models import Contact
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction

@csrf_exempt
def identify(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            phone_number = str(data.get('phoneNumber')) if data.get('phoneNumber') else None

            if not email and not phone_number:
                return JsonResponse({"error": "At least email or phoneNumber is required"}, status=400)

            # Fetch contacts matching email or phoneNumber
            email_contacts = Contact.objects.filter(email=email) if email else Contact.objects.none()
            phone_contacts = Contact.objects.filter(phoneNumber=phone_number) if phone_number else Contact.objects.none()

            # Gather all contacts
            all_contacts = list(email_contacts) + list(phone_contacts)

            if not all_contacts:
                # No matching contacts, create a new primary contact
                new_contact = Contact.objects.create(
                    email=email,
                    phoneNumber=phone_number,
                    linkPrecedence='primary'
                )
                return JsonResponse({
                    "contact": {
                        "primaryContatctId": new_contact.id,
                        "emails": [new_contact.email] if new_contact.email else [],
                        "phoneNumbers": [new_contact.phoneNumber] if new_contact.phoneNumber else [],
                        "secondaryContactIds": []
                    }
                })

            # Find unique primary contacts
            primary_contacts = set()
            secondary_contacts = []

            for contact in all_contacts:
                if contact.linkPrecedence == 'primary':
                    primary_contacts.add(contact)
                elif contact.linkedId:
                    primary_contacts.add(contact.linkedId)
                    secondary_contacts.append(contact)

            primary_contacts = sorted(primary_contacts, key=lambda x: x.createdAt)

            # Determine the oldest primary contact
            main_primary_contact = primary_contacts[0]

            # Merge all other primary contacts into this main primary contact
            other_primary_contacts = primary_contacts[1:]

            with transaction.atomic():
                for other_primary in other_primary_contacts:
                    Contact.objects.filter(linkedId=other_primary).update(linkedId=main_primary_contact)
                    other_primary.linkPrecedence = 'secondary'
                    other_primary.linkedId = main_primary_contact
                    other_primary.save()

            # Fetch all secondary contacts for the main primary contact (after merging)
            secondary_contacts = Contact.objects.filter(linkedId=main_primary_contact)

            # Build the response
            response_data = {
                "contact": {
                    "primaryContatctId": main_primary_contact.id,
                    "emails": list(set(
                        [main_primary_contact.email] +
                        [c.email for c in secondary_contacts if c.email]
                    )),
                    "phoneNumbers": list(set(
                        [main_primary_contact.phoneNumber] +
                        [c.phoneNumber for c in secondary_contacts if c.phoneNumber]
                    )),
                    "secondaryContactIds": [c.id for c in secondary_contacts]
                }
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    elif request.method == 'GET':
#         # Handle GET request to return all contacts (for viewing/debugging purposes)
        try:
            contacts = Contact.objects.all()
            contacts_data = []
            for contact in contacts:
                contacts_data.append({
                    "id": contact.id,
                    "email": contact.email,
                    "phoneNumber": contact.phoneNumber,
                    "linkedId": contact.linkedId.id if contact.linkedId else None,
                    "linkPrecedence": contact.linkPrecedence,
                    "createdAt": contact.createdAt,
                    "updatedAt": contact.updatedAt,
                    "deletedAt": contact.deletedAt,
                })

            return JsonResponse({"contacts": contacts_data}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)
