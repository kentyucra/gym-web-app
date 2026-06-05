import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.routes.auth import error_response

muscles_bp = Blueprint("muscles", __name__)

MUSCLE_ALIASES = {
    "abs": "Rectus abdominis",
    "abdominals": "Rectus abdominis",
    "back": "Latissimus dorsi",
    "biceps": "Biceps brachii",
    "calves": "Gastrocnemius muscle",
    "chest": "Pectoralis major",
    "front delt": "Deltoid muscle",
    "front delts": "Deltoid muscle",
    "glutes": "Gluteus maximus",
    "hamstrings": "Hamstring",
    "lats": "Latissimus dorsi",
    "lower chest": "Pectoralis major",
    "lower traps": "Trapezius",
    "middle chest": "Pectoralis major",
    "pec": "Pectoralis major",
    "pecs": "Pectoralis major",
    "quads": "Quadriceps femoris muscle",
    "rear delt": "Deltoid muscle",
    "rear delts": "Deltoid muscle",
    "shoulder": "Deltoid muscle",
    "shoulders": "Deltoid muscle",
    "side delt": "Deltoid muscle",
    "side delts": "Deltoid muscle",
    "traps": "Trapezius",
    "triceps": "Triceps brachii",
    "upper back": "Trapezius",
    "upper chest": "Pectoralis major",
    "upper traps": "Trapezius",
}


def fetch_wikipedia_summary(page_name):
    encoded_name = quote(page_name)
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_name}"
    wikipedia_request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "SiteFitnessWebApp/1.0 local-development",
        },
    )

    with urlopen(wikipedia_request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def search_wikipedia_page(search_term):
    params = urlencode(
        {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": f"{search_term} muscle anatomy",
            "srlimit": 1,
        }
    )
    url = f"https://en.wikipedia.org/w/api.php?{params}"
    wikipedia_request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "SiteFitnessWebApp/1.0 local-development",
        },
    )

    with urlopen(wikipedia_request, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))

    results = data.get("query", {}).get("search", [])
    if not results:
        return None

    return results[0].get("title")


def candidate_page_names(muscle_name):
    normalized = " ".join(muscle_name.lower().split())
    candidates = []

    if normalized in MUSCLE_ALIASES:
        candidates.append(MUSCLE_ALIASES[normalized])

    if normalized.startswith("muscle "):
        stripped_name = normalized.removeprefix("muscle ").strip()
        if stripped_name in MUSCLE_ALIASES:
            candidates.append(MUSCLE_ALIASES[stripped_name])
        candidates.append(stripped_name)

    candidates.append(muscle_name)

    seen = set()
    unique_candidates = []
    for candidate in candidates:
        candidate_key = candidate.lower()
        if candidate_key not in seen:
            seen.add(candidate_key)
            unique_candidates.append(candidate)

    return unique_candidates


def find_wikipedia_summary(muscle_name):
    for candidate in candidate_page_names(muscle_name):
        try:
            return fetch_wikipedia_summary(candidate), candidate, "alias_or_exact"
        except HTTPError as error:
            if error.code != 404:
                raise

    search_title = search_wikipedia_page(muscle_name)
    if search_title:
        return fetch_wikipedia_summary(search_title), search_title, "search"

    raise HTTPError("", 404, "No Wikipedia page found", None, None)


@muscles_bp.get("/muscles/image")
@jwt_required()
def get_muscle_image():
    """Find a muscle image from Wikipedia.
    ---
    tags:
      - Muscles
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: name
        required: true
        schema:
          type: string
        description: Muscle name, for example Biceps brachii.
    responses:
      200:
        description: Muscle image result.
      400:
        description: Missing muscle name.
      404:
        description: Wikipedia page was not found.
    """
    muscle_name = (request.args.get("name") or "").strip()
    if not muscle_name:
        return error_response("Muscle name is required.", 400)

    try:
        data, matched_name, match_type = find_wikipedia_summary(muscle_name)
    except HTTPError as error:
        if error.code == 404:
            return error_response("No Wikipedia page was found for that muscle.", 404)
        return error_response("Wikipedia did not return a usable response.", 502)
    except (TimeoutError, URLError):
        return error_response("Wikipedia is not reachable right now.", 502)

    image = data.get("originalimage") or data.get("thumbnail") or {}
    content_urls = data.get("content_urls") or {}
    desktop_urls = content_urls.get("desktop") or {}

    return jsonify(
        {
            "muscle": {
                "name": muscle_name,
                "matchedName": matched_name,
                "matchType": match_type,
                "title": data.get("title"),
                "description": data.get("description"),
                "extract": data.get("extract"),
                "imageUrl": image.get("source"),
                "pageUrl": desktop_urls.get("page"),
                "source": "wikipedia",
            }
        }
    )
