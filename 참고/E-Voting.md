# Electronic Voting
[참고1](https://crypto.stanford.edu/pbc/notes/crypto/voting.html), [참고2](http://web.mit.edu/6.857/OldStuff/Fall02/handouts/L15-voting.pdf), [참고3](http://openstorage.mercubuana.ac.id/files/openjournal/JournalOfDesignB/13/5_653.pdf)


## Blind Signatures(은닉서명)

(참고2) RSA는 곱셈에 대해 Homomorphic하다.<br>
(참고2) 은닉 서명을 이용하면 서명자가 내용을 알 수 없지만 서명할 수 있다.

* 선거 관리자가 공개키를 게시한다.(Pk = {e, N}, Sk = {d, N})
* 투표자는 자신의 ID로 쓸 랜덤한 숫자(ID)를 정한다.
* 각 옵션에 해당하는 토큰을 만들기 위해 투표자는 자신의 ID를 모든 선택지 뒤에 붙인다.(m) (e.g. "Bush" || ID, "Gore" || ID)
* 투표자는 인증을 위한 개인 정보와 Blinded Token<sup>1)</sup>들을 보낸다.
* 투표자는 토큰이 제대로 구성되었다는 것에 대한 Zero-Knowledge Proof를 제출한다.
* 선거 관리자는 투표자의 토큰이 제대로 구성되었음을 확인하고 모든 Blinded Token에 서명(σ)한다.
* 투표자는 모든 서명을 unblind<sup>2)</sup> 한다.
* 투표를 하기 위해 선거 관리자의 서명과 토큰 하나를 집계기관에 제출한다.

<sup>1)</sup> 랜덤한 숫자(r)을 이용한 m·r<sup>e</sup><br>
<sup>2)</sup> σ(m·r<sup>e</sup>) = σ(m) · σ(r<sup>e</sup>) = σ(m) · (r<sup>e·d</sup> mod N) = σ(m) · r

## Cryptograghic Counters
* 숫자 B의 Cryptograghic Counter는 3개의 알고리즘으로 구성된다
    * Generate: (Pk, Sk, S<sub>0</sub>) ∈ {0, 1}<sup>*</sup>, S<sub>0</sub>는 암호화된 카운터의 initial state
    * Decrpyt: Dec(S, Sk) = one of 0, 1, 2, ···, B. Dec(S<sub>0</sub>, Sk) = 0
    * Increment: Dec(Inc(S), Sk) = Dec(S, Sk) + 1

* ???
* 예시1. Additively homomorphic encryption
* 예시2. Ostrovski-Katz



## Mix Nets
* 타인이 투표값을 알 수 없도록 암호화 사용
* 악의적인 집계자가 특정 투표자의 투표값을 알 수 없도록 mix-net을 사용
* 표 값을 서로 섞고, 표가 올바르게 섞였음을 Zero-Knowledge Proof를 이용해 증명

## [Zero-Knowledge Proof](https://medium.com/decipher-media/zero-knowledge-proof-chapter-2-deep-dive-into-zk-snarks-f8b16e1b7b4c)
* 투표자 n명의 ID를 받음(v<sub>1</sub>, v<sub>2</sub>, ···, v<sub>n</sub>)
* y = (x-v<sub>1</sub>)(x-v<sub>2</sub>)···(x-v<sub>n</sub>), y = 0
* 위 식을 만족하는 특정한 x값을 zk-SNARKs를 통해 검증
* 검증이 완료되면 검증에 사용된 값을 저장하여 같은 값으로 또 검증하는 것을 방지
* 검증된 사용자에게 지갑 주소를 받아 투표자로 컨트랙트에 등록
* Zero-Knowlegde Proof를 통해 사용자-지갑주소 사이 연결을 끊을 수 있음
