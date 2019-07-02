pragma solidity >=0.4.21 <0.6.0;

import './Ballot.sol';

contract ElectionCreation {
    address[] public deployedBallots;
    constructor (bytes32[] memory candidates, bytes32[] memory district, uint hour) public {
        for(uint i = 0; i < district.length; i++){
            address newBallot = new Ballot(candidates, district[i], msg.sender, hour);
            deployedBallots.push(newBallot);
        }
    }
    function getDeployedBallots() public view returns(address[] memory) {
        return deployedBallots;
    }
}
