import re


def mask_phi(text):

    mappings = {}

    patient_names = re.findall(
        r"Patient Name:\s*(.*)",
        text
    )

    count = 1

    for name in patient_names:

        token = f"[PATIENT_{count:03d}]"

        mappings[token] = name

        text = text.replace(
            name,
            token
        )

        count += 1

    mrns = re.findall(
        r"MRN:\s*(\d+)",
        text
    )

    count = 1

    for mrn in mrns:

        token = f"[MRN_{count:03d}]"

        mappings[token] = mrn

        text = text.replace(
            mrn,
            token
        )

        count += 1

    return text, mappings

def unmask_phi(
    text,
    mappings
):

    for token, original in mappings.items():

        text = text.replace(
            token,
            original
        )

    return text