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
