from typing import List
from openai import OpenAI

# ---------------------------------------------------------------------------
# Knowledge base
# Each chunk is tagged so the retriever can score it against a pet's profile.
# Tags draw from: species, age group, task category, breed words, health conditions.
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE: List[dict] = [
    # --- DOGS: walking ---
    {
        "tags": ["dog", "walk"],
        "text": (
            "Adult dogs need 30–60 minutes of walking per day, ideally split into two sessions "
            "(morning and evening) to support digestion and steady energy levels. Skipping walks "
            "leads to restlessness, destructive behaviour, and weight gain."
        ),
    },
    {
        "tags": ["dog", "walk", "puppy"],
        "text": (
            "Puppies under 12 months should follow the 5-minute rule: no more than 5 minutes of "
            "structured exercise per month of age, twice daily. Over-exercising puppies risks "
            "permanent damage to growth plates in developing joints."
        ),
    },
    {
        "tags": ["dog", "walk", "senior"],
        "text": (
            "Senior dogs (8+ years) still need daily movement but benefit from shorter, more "
            "frequent walks (15–20 minutes twice daily) rather than one long session, to maintain "
            "joint mobility without causing post-exercise fatigue or soreness."
        ),
    },
    # --- DOGS: feeding ---
    {
        "tags": ["dog", "feeding"],
        "text": (
            "Most adult dogs do best on two meals per day spaced 8–12 hours apart. Consistent "
            "feeding times regulate digestion and reduce the risk of bloat (GDV), particularly "
            "in large-breed and deep-chested dogs."
        ),
    },
    {
        "tags": ["dog", "feeding", "puppy"],
        "text": (
            "Puppies under 6 months need three meals per day to support rapid growth and prevent "
            "hypoglycaemia. Transitioning to two meals is appropriate around 6 months of age."
        ),
    },
    # --- DOGS: grooming ---
    {
        "tags": ["dog", "grooming"],
        "text": (
            "Brushing frequency depends on coat type: short coats (Beagle, Labrador) need weekly "
            "brushing; medium coats (Border Collie) benefit from 2–3 times per week; long or "
            "double coats (Husky, Golden Retriever) need daily brushing to prevent matting."
        ),
    },
    # --- DOGS: meds ---
    {
        "tags": ["dog", "meds"],
        "text": (
            "Medications should be given at the same time each day to maintain stable therapeutic "
            "blood levels. Administering with food (unless the vet instructs otherwise) reduces "
            "gastric upset and improves a dog's willingness to take the medication."
        ),
    },
    # --- DOGS: enrichment ---
    {
        "tags": ["dog", "enrichment"],
        "text": (
            "Mental enrichment is as important as physical exercise for dogs. Puzzle feeders, "
            "short training sessions (10–15 minutes), and scent-work games reduce anxiety and "
            "boredom-driven destructiveness. Mid-morning is an ideal time when dogs are most alert."
        ),
    },
    # --- DOGS: breeds ---
    {
        "tags": ["dog", "beagle"],
        "text": (
            "Beagles are scent hounds with high energy and a powerful nose. They need at least "
            "60 minutes of exercise daily and are prone to obesity when under-exercised. "
            "Leash walks are essential — Beagles will follow a scent trail and ignore recall commands."
        ),
    },
    {
        "tags": ["dog", "labrador", "retriever"],
        "text": (
            "Labradors need 60–80 minutes of vigorous exercise daily. They are prone to hip "
            "dysplasia and obesity; measured feeding (no free-feeding) combined with regular "
            "exercise is critical for long-term joint and weight health."
        ),
    },
    {
        "tags": ["dog", "chihuahua"],
        "text": (
            "Chihuahuas need shorter walks (20–30 minutes daily) and are prone to hypoglycaemia, "
            "especially as puppies. Consistent meal times and watching for shivering or weakness "
            "are important signs of low blood sugar."
        ),
    },
    {
        "tags": ["dog", "golden", "retriever"],
        "text": (
            "Golden Retrievers require 60–90 minutes of exercise daily. They are prone to hip "
            "dysplasia and obesity; maintaining a healthy weight through regular exercise and "
            "measured feeding is one of the highest-impact preventive health steps."
        ),
    },
    # --- CATS: feeding ---
    {
        "tags": ["cat", "feeding"],
        "text": (
            "Cats are obligate carnivores and do best on 2–3 small measured meals per day rather "
            "than free-feeding, which contributes to feline obesity. Wet food supports hydration, "
            "which is critical for urinary tract health in cats."
        ),
    },
    {
        "tags": ["cat", "feeding", "senior"],
        "text": (
            "Senior cats (11+ years) often have reduced kidney function and benefit from wet-food "
            "diets with controlled phosphorus. Smaller, more frequent meals help maintain weight "
            "as older cats absorb nutrients less efficiently."
        ),
    },
    # --- CATS: grooming ---
    {
        "tags": ["cat", "grooming"],
        "text": (
            "Short-haired cats groom themselves effectively but benefit from weekly brushing to "
            "reduce hairballs. Long-haired breeds (Persian, Maine Coon) need daily brushing to "
            "prevent painful matting, especially around the collar and hindquarters."
        ),
    },
    # --- CATS: enrichment ---
    {
        "tags": ["cat", "enrichment"],
        "text": (
            "Indoor cats need 15–30 minutes of interactive play per day to prevent boredom and "
            "obesity. Schedule play in the morning and evening when cats are naturally most active "
            "(crepuscular pattern). Wand toys, puzzle feeders, and window perches all help."
        ),
    },
    # --- CATS: meds ---
    {
        "tags": ["cat", "meds"],
        "text": (
            "Giving medication to cats is most effective when paired with a high-value treat or "
            "pill pocket. Consistent timing — ideally tied to a meal — improves compliance and "
            "maintains stable therapeutic drug levels."
        ),
    },
    # --- RABBITS ---
    {
        "tags": ["rabbit", "feeding"],
        "text": (
            "Rabbits need unlimited timothy hay (80% of their diet) available at all times for "
            "dental wear and gut motility. Fresh leafy greens (1–2 cups per 5 lbs body weight "
            "daily) and a small measured serving of pellets complete the diet. Avoid sugary treats."
        ),
    },
    {
        "tags": ["rabbit", "enrichment"],
        "text": (
            "Rabbits need 3–4 hours of free-roaming exercise outside their enclosure each day. "
            "Schedule this in the early morning and late afternoon when rabbits are naturally "
            "most active. Tunnels, chew toys, and digging boxes provide essential enrichment."
        ),
    },
    {
        "tags": ["rabbit", "grooming"],
        "text": (
            "Short-haired rabbits need brushing once a week; long-haired breeds (Angora) require "
            "daily brushing to prevent wool block, a potentially fatal GI obstruction. Never "
            "bathe a rabbit — it causes extreme stress and hypothermia risk."
        ),
    },
    # --- BIRDS ---
    {
        "tags": ["bird", "feeding"],
        "text": (
            "Pet birds should receive fresh food twice daily; uneaten food must be removed after "
            "2–4 hours to prevent bacterial growth. A balanced diet includes pellets, fresh "
            "vegetables, and limited fruit. Seeds-only diets cause serious nutritional deficiencies."
        ),
    },
    {
        "tags": ["bird", "enrichment"],
        "text": (
            "Parrots and other intelligent birds need 2–4 hours of out-of-cage time and direct "
            "social interaction daily. Short training sessions (10–15 minutes) and foraging "
            "enrichment prevent feather-destructive behaviours linked to boredom."
        ),
    },
    # --- HEALTH CONDITIONS ---
    {
        "tags": ["diabetes", "meds", "feeding"],
        "text": (
            "Diabetic pets must receive insulin at the same time each day, immediately after a "
            "full meal, to avoid dangerous hypoglycaemia. Meal size and timing must be strictly "
            "consistent — variation directly undermines insulin dosing accuracy."
        ),
    },
    {
        "tags": ["arthritis", "joint", "walk"],
        "text": (
            "Pets with arthritis benefit from shorter, more frequent low-impact exercise rather "
            "than long intense sessions. A brief warm-up before walks and avoiding hard surfaces "
            "reduce joint stress. Anti-inflammatory medications or joint supplements should be "
            "given with food at a consistent time."
        ),
    },
    {
        "tags": ["dental", "grooming"],
        "text": (
            "Dental disease is the most preventable condition in pets. Daily tooth brushing "
            "reduces plaque accumulation by up to 70% compared to weekly brushing. Pairing "
            "dental care with another routine task (e.g. after a walk) builds a lasting habit."
        ),
    },
    {
        "tags": ["anxiety", "enrichment", "dog"],
        "text": (
            "Dogs with separation anxiety benefit most from a predictable daily routine — consistent "
            "walk and feeding times significantly reduce anticipatory stress. Mental enrichment "
            "(Kong toys, puzzle feeders) before the owner leaves redirects anxious energy."
        ),
    },
    {
        "tags": ["kidney", "feeding", "cat"],
        "text": (
            "Cats with chronic kidney disease (CKD) need increased water intake; wet-food diets "
            "and running-water fountains meaningfully improve hydration. Phosphorus restriction "
            "is critical — standard cat food is typically too high in phosphorus for CKD patients."
        ),
    },
    {
        "tags": ["eye", "drops", "meds"],
        "text": (
            "Eye drops are most effective when given at the same time each day and away from "
            "stressful events. Pair the task with a high-value reward to build a positive "
            "association and reduce handling resistance over time."
        ),
    },
]

# ---------------------------------------------------------------------------
# Default model presets (OpenRouter model IDs)
# ---------------------------------------------------------------------------

ALL_PRESET_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-31b-it:free",
    "openai/gpt-oss-20b:free",
]


class PetCareRAG:
    """Retrieval-augmented pet care advisor backed by any OpenRouter model.

    retrieve() scores every knowledge chunk against the pet's profile (species,
    age group, breed words, task categories, special-need keywords) and returns
    the top-k most relevant chunks as plain text. generate_advice() sends those
    chunks to the chosen LLM as the sole factual source, so the model's output
    is grounded in retrieved guidelines rather than general training knowledge.
    """

    def __init__(self, api_key: str, model: str, top_k: int = 5):
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self._model = model
        self._top_k = top_k

    def retrieve(self, pet, tasks: list) -> List[str]:
        """Score every knowledge chunk against the pet's profile + task set.
        Returns the top-k most relevant chunks as plain text strings."""
        if pet.species.lower() == "cat":
            age_group = "puppy" if pet.age < 1 else "senior" if pet.age >= 11 else "adult"
        else:
            age_group = "puppy" if pet.age < 1 else "senior" if pet.age >= 8 else "adult"

        query_tags: set = {
            pet.species.lower(),
            age_group,
            *(t.category.lower() for t in tasks),
        }
        # Split breed into individual words so "Golden Retriever" → {"golden", "retriever"}
        query_tags |= {w.lower() for w in pet.breed.split()}
        # Split each special need so "kidney disease" → {"kidney", "disease"}
        for need in pet.special_needs:
            query_tags |= {w.lower() for w in need.split()}

        scored: list = []
        for chunk in KNOWLEDGE_BASE:
            score = len(set(chunk["tags"]) & query_tags)
            if score > 0:
                scored.append((score, chunk["text"]))

        scored.sort(key=lambda x: -x[0])
        return [text for _, text in scored[: self._top_k]]

    def generate_advice(self, pet, owner, schedule) -> str:
        """Retrieve relevant guidelines then call the LLM to produce expert,
        grounded advice. The model is instructed to cite specific retrieved
        guidelines rather than relying on general training knowledge.

        Falls back to a plain message if no relevant guidelines are found.
        """
        tasks = [st.task for st in schedule.scheduled_tasks]
        retrieved = self.retrieve(pet, tasks)

        if not retrieved:
            return (
                f"No specific guidelines found for {pet.name}'s profile. "
                "The schedule was built on priority and time-availability rules."
            )

        schedule_lines = [
            f"  {st.time_slot} — {st.task.name} "
            f"(category: {st.task.category}, {st.task.duration} min, priority {st.task.priority})"
            for st in sorted(schedule.scheduled_tasks, key=lambda x: x.time_slot)
        ] or ["  No tasks could be scheduled within the available time."]

        guidelines_text = "\n\n".join(
            f"[Guideline {i + 1}] {chunk}" for i, chunk in enumerate(retrieved)
        )

        prompt = f"""You are an expert veterinary care advisor helping pet owners understand and improve their pet's daily care schedule.

## Pet Profile
- Name: {pet.name}
- Species: {pet.species}
- Breed: {pet.breed}
- Age: {pet.age} year(s)
- Special needs: {", ".join(pet.special_needs) if pet.special_needs else "none"}

## Owner Context
- Name: {owner.name}
- Time available today: {owner.time_available} minutes
- Preferences: {", ".join(owner.preferences) if owner.preferences else "none specified"}

## Today's Generated Schedule
{chr(10).join(schedule_lines)}

## Retrieved Pet Care Guidelines
Use these as your primary and only factual source:

{guidelines_text}

## Instructions
Write a concise expert analysis (3–5 bullet points) of today's schedule grounded in the retrieved guidelines above. For each point:
- Reference which guideline supports your observation (e.g. "Per Guideline 2...")
- Explain whether a task is appropriately timed, sufficient, or misaligned with expert recommendations for {pet.name} specifically
- Flag any gap between what the guidelines recommend and what is currently scheduled
- Offer one concrete, actionable suggestion where the schedule could better serve {pet.name}

Do not repeat the schedule. Do not introduce facts not present in the retrieved guidelines. Address {owner.name} directly and keep the tone warm but precise."""

        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
