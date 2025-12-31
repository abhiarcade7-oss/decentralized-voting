// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ManagedElection {

    // =====================================================
    // 🗳️ ELECTION STATE
    // =====================================================
    uint256 public candidateCount;
    uint256 public totalVotes;

    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // =====================================================
    // 🧑‍💼 CANDIDATE STRUCT
    // =====================================================
    struct Candidate {
        uint256 id;           // on-chain candidate ID
        string name;          // candidate name
        uint256 voteCount;    // votes received
        bool isActive;        // active / deactivated
    }

    // candidateId => Candidate
    mapping(uint256 => Candidate) public candidates;

    // voterHash => has voted?
    mapping(bytes32 => bool) public hasVoted;

    // =====================================================
    // 🔐 MODIFIER
    // =====================================================
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner allowed");
        _;
    }

    // =====================================================
    // 📢 EVENTS (VERY IMPORTANT FOR AUDIT)
    // =====================================================
    event CandidateAdded(uint256 indexed id, string name);
    event CandidateDeactivated(uint256 indexed id);
    event VoteCast(bytes32 indexed voterHash, uint256 indexed candidateId);

    // =====================================================
    // ➕ ADD CANDIDATE (ADMIN / BACKEND)
    // =====================================================
    function addCandidate(string calldata _name) external onlyOwner {
        require(bytes(_name).length > 0, "Candidate name required");

        candidateCount++;

        candidates[candidateCount] = Candidate({
            id: candidateCount,
            name: _name,
            voteCount: 0,
            isActive: true
        });

        emit CandidateAdded(candidateCount, _name);
    }

    // =====================================================
    // ❌ DEACTIVATE CANDIDATE (NO DELETE)
    // =====================================================
    function deactivateCandidate(uint256 _candidateId) external onlyOwner {
        require(
            _candidateId > 0 && _candidateId <= candidateCount,
            "Invalid candidate"
        );
        require(candidates[_candidateId].isActive, "Already inactive");

        candidates[_candidateId].isActive = false;

        emit CandidateDeactivated(_candidateId);
    }

    // =====================================================
    // 🗳️ CAST VOTE (ONE PERSON = ONE VOTE)
    // =====================================================
    function vote(bytes32 _voterHash, uint256 _candidateId) external {
        require(_voterHash != bytes32(0), "Invalid voter");
        require(!hasVoted[_voterHash], "Already voted");

        require(
            _candidateId > 0 && _candidateId <= candidateCount,
            "Invalid candidate"
        );
        require(candidates[_candidateId].isActive, "Candidate inactive");

        hasVoted[_voterHash] = true;
        candidates[_candidateId].voteCount += 1;
        totalVotes += 1;

        emit VoteCast(_voterHash, _candidateId);
    }

    // =====================================================
    // 📊 GET CANDIDATE DETAILS
    // =====================================================
    function getCandidate(uint256 _candidateId)
        external
        view
        returns (
            uint256 id,
            string memory name,
            uint256 voteCount,
            bool isActive
        )
    {
        require(
            _candidateId > 0 && _candidateId <= candidateCount,
            "Invalid candidate"
        );

        Candidate memory c = candidates[_candidateId];
        return (c.id, c.name, c.voteCount, c.isActive);
    }

    // =====================================================
    // 📈 GET VOTES ONLY
    // =====================================================
    function getVotes(uint256 _candidateId)
        external
        view
        returns (uint256)
    {
        require(
            _candidateId > 0 && _candidateId <= candidateCount,
            "Invalid candidate"
        );
        return candidates[_candidateId].voteCount;
    }
}
