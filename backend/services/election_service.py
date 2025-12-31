from backend.models import Election, Candidate
from backend.database import db
from .blockchain_service import BlockchainService
import os
import random



# =====================================================
# ⭐ STEP 2 — UNIQUE 4–8 digit election ID generator
# =====================================================
def generate_unique_election_id():
    """Generates a random 4 to 8 digit election ID."""
    return random.randint(1000, 99999999)


class ElectionService:

    def __init__(self):
        self.bc_service = BlockchainService()

    # =====================================================
    # ====================== ELECTION ======================
    # =====================================================

    def create_election(self, name):
        """
        Creates a new election by deploying blockchain contract
        and storing election record in database.
        """

        owner_address = os.getenv("OWNER_ADDRESS")
        private_key = os.getenv("PRIVATE_KEY")

        contract_address = None

        # Blockchain deployment (safe check)
        if owner_address and private_key:
            contract_address, _ = self.bc_service.deploy_contract(
                owner_address,
                private_key
            )

        # ⭐ NEW FIELD: election_id (4–8 digit unique)
        unique_id = generate_unique_election_id()

        election = Election(
            name=name,
            contract_address=contract_address,
            is_active=False,
            unique_id=unique_id    # ← Added unique election ID
        )

        db.session.add(election)
        db.session.commit()

        return election

    def get(self, election_id):
        return Election.query.get(election_id)

    def get_active(self):
        return Election.query.filter_by(is_active=True).first()

    def set_active(self, election_id):
        """
        Sets one election active and deactivates all others.
        """
        Election.query.update({Election.is_active: False})

        election = self.get(election_id)
        if election:
            election.is_active = True
            db.session.commit()

        return election

    def deactivate_all(self):
        """Turns off all elections."""
        Election.query.update({Election.is_active: False})
        db.session.commit()

    def get_all_elections(self):
        return Election.query.all()

    # =====================================================
    # ==================== CANDIDATES =====================
    # =====================================================

    def add_candidate_record(
        self,
        name,
        party,
        photo,
        logo,
        election_id,
        on_chain_id=0
    ):
        """Adds candidate into database."""

        candidate = Candidate(
            name=name,
            party=party,
            photo=photo,
            logo=logo,
            election_id=election_id,
            on_chain_id=on_chain_id
        )

        db.session.add(candidate)
        db.session.commit()

        return candidate

    def get_candidates_by_election(self, election_id):
        return Candidate.query.filter_by(election_id=election_id).all()

    def get_candidate_by_id(self, candidate_id):
        """Fetch single candidate by ID."""
        return Candidate.query.get(candidate_id)

    def delete_candidate(self, candidate_id):
        """Delete candidate from database."""

        candidate = Candidate.query.get(candidate_id)

        if not candidate:
            return False

        db.session.delete(candidate)
        db.session.commit()
        return True

    # =====================================================
    # ====================== RESULTS ======================
    # =====================================================

    def get_results_for_election(self, election_id):
        """
        Fetch voting result for election.
        Supports both blockchain and local DB.
        """

        candidates = Candidate.query.filter_by(
            election_id=election_id
        ).all()

        results = []

        for c in candidates:
            results.append({
                "id": c.id,
                "name": c.name,
                "party": c.party,
                "votes": c.vote_count if hasattr(c, "vote_count") else 0,
                "photo": c.photo,
                "logo": c.logo
            })

        return results
