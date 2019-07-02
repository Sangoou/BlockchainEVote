pragma solidity >=0.4.21 <0.6.0;

contract Ballot {
    struct Candidates {
        bytes32 name;
        uint voteCount;
        uint creationDate;
        uint expirationDate;
    }

    Candidates[] public candidates;
    address public manager;
    bytes32 public votingDistrict;
    mapping(address => bool) public voters;

    modifier restricted() {
        require(
            msg.sender == manager,
            'Sender is not manager'
        );
       _;
    }

    constructor (bytes32[] memory candidateNames, bytes32 district, address creator, uint amountOfHours) public {
        manager = creator;
        votingDistrict = district;
        for (uint i = 0; i < candidateNames.length; i++) {
            candidates.push(Candidates({
                name: candidateNames[i],
                voteCount: 0,
                creationDate: now,
                expirationDate: now + amountOfHours
            }));
        }
    }
    function vote(uint candidate) public{
        require(!voters[msg.sender]);
        if(now > candidates[candidate].expirationDate){
            revert();
        }
        candidates[candidate].voteCount += 1;
        voters[msg.sender] = true;
    }
    function getCandidateName(uint candidate) public restricted view returns (bytes32){
        require(now > candidates[candidate].expirationDate);
        return candidates[candidate].name;
    }
    function getVoteCount(uint candidate) public restricted view returns (uint) {
        require(now > candidates[candidate].expirationDate);
        return candidates[candidate].voteCount;
    }
}
