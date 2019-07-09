pragma solidity >=0.4.21 <0.6.0;
pragma experimental ABIEncoderV2;

contract Vote {
    enum VoteState { PENDING, PROCEEDING, CLOSED }

    VoteState _voteState;
    address _voteOwner;
    string[] _options;
    uint _deadline;
    address[] _voters;
    mapping(address => bool) _ballots;
    string[] _tickets;

    string _publicKey;
    string _privateKey;

    constructor() public {
        _voteState = VoteState.CLOSED;
        _voteOwner = address(0);
    }

    modifier voteOwnerOnly() {
        require(msg.sender == _voteOwner, "You are Not Owner!");
        _;
    }

    function createVote(string[] memory options, uint deadline, string memory publicKey) public {
        require(_voteState == VoteState.CLOSED, "Voting is Not Closed");
        require(deadline > now, "Deadline is Past");

        delete _options;
        delete _voters;
        delete _tickets;
        _publicKey = publicKey;
        _privateKey = "";

        for(uint i = 0; i < options.length; i++){
            _options.push(options[i]);
        }

        _deadline = deadline;
        _voteOwner = msg.sender;
        _voteState = VoteState.PENDING;
    }

    function registerVoter(address voter) public voteOwnerOnly {
        require(_voteState == VoteState.PENDING, "Voting is Not Pending");
        _voters.push(voter);
        _ballots[voter] = true;
    }

    function openVoting() public voteOwnerOnly {
        require(_voteState == VoteState.PENDING, "Voting is Not Pending");
        _voteState = VoteState.PROCEEDING;
    }

    function vote(string memory choice) public {
        require(_voteState == VoteState.PROCEEDING && now <= _deadline, "Voting is Not Proceeding");
        require(_ballots[msg.sender], "Your don't have Voting Permission or Already vote");

        _tickets.push(choice);
        _ballots[msg.sender] = false;
    }

    function closeVoting(string memory privateKey) public voteOwnerOnly {
        require(_voteState == VoteState.PROCEEDING, "Voting is Not Proceeding");
        require(now > _deadline, "Deadline is not reached");

        _privateKey = privateKey;
        _voteState = VoteState.CLOSED;
    }

    // 이하 컨트랙트 내부 변수 확인을 위한 함수들.
    function getPublicKey() public view returns(string memory publicKey) {
        return _publicKey;
    }

    function getPrivateKey() public view returns(string memory privateKey) {
        return _privateKey;
    }

    function getOptions() public view returns(string[] memory options) {
        return _options;
    }

    function getDeadline() public view returns(uint deadline) {
        require(_voteState != VoteState.CLOSED, "Voting is Closed");
        return _deadline;
    }

    function getTickets() public view returns(string[] memory tickets){
        require(_voteState == VoteState.CLOSED, "Voteing is Not Closed");
        return _tickets;
    }

    function getState() public view returns(VoteState state){
        return _voteState;
    }
}