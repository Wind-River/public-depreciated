# SParts Project: Software Parts Ledger
### Utilizing the Blockchain to Establish Trust with Open Source across a SupplyChain

## Introduction

We developed a Blockchain-based Software Parts Ledger to track the open source components from which today's manufactured products and devices are constructed. A number of important benefits are obtained by knowing which open source components are used such as: 1) ensuring manufactures are able to identify and secure the distribution rights (licenses) for all open source components; 2) understanding the impact of open source security vulnerabilities; 3) enable identification of cryptography technologies (e.g., FIPS 140-2 certification, export licensing); and 4) enable accurate reporting on all open source parts as a requirement to obtaining functional safety certification for safety critical products (e.g., medical devices, aircraft, autonomous vehicles, elevators, …)

The Software Part ledger establishes trust between a manufacture and its suppliers by tracking suppliers, their software parts, the open source used and the corresponding **Compliance Artifacts** - e.g., source code, legal notices, Open Source Bill of Materials, SPDX data, cryptography data and so forth. This is particular helpful for manufactures who build products that utilize software from many different suppliers (including sub-suppliers). To achieve accountability a mechanism is needed to maintain global state information about the suppliers; their parts and compliance artifacts for all participate across the supply chain. To establish trust among all participants, these records need to be i) transparent, ii) immutable, while iii) removing the dependence on third party information brokers (middle guy).

We obtain the required level of trust by utilizing the Hyperledger project's Sawtooth platform to construct a Blockchain Ledger. The Ledger achieves accountability by tracking which suppliers delivered which software parts that used which open source and who delivered (or did not deliver) which open source compliance artifacts. We also utilize a new data construct, the **Compliance Envelope**, a standard method of collecting, indexing and archiving a diverse collection of compliance artifacts so that they can be delivered as a single unit with each software part. A compliance envelope is essentially an archive file containing the collection of artifacts plus a set meta information. We use the Ledger to maintain the association among the supplier, their parts and the corresponding compliance envelope. One can associate individual artifacts to a given product but that adds an addition level of information retrieval complexity. The Software Parts Ledger ensures the compliance envelope information is transparent, immutable to unlawful modifications and where no central organization broker is required. 

## Example Illustration

The biggest challenge to obtaining a complete Open Source Bill of Materials (OSS-BOM) for manufactured products (along with the corresponding compliance artifacts) arises because software parts are provided by multiple different suppliers and sub-suppliers. Consider the simple example illustrated below where three different suppliers provide software parts used in the manufacturing of a video camera V sold by manufacturer M. Supplier S1 delivers the microprocessor accompanied by the firmware and software drivers. Supplier S2 assembles and delivers the Linux runtime operating system and Supplier S3 delivers the applications that manage the camera display, menu and various functions. Ideally, when camera V ships, it should be accompanied by a single compliance envelope that contains, as a minimum, a list of all the open source parts incorporated by the various suppliers (OSS BOMs); the mandatory source code and legal notices.

<p align="center"><img src="./docs/images/video-camera-arch.png" width="710" height="475"/>
<br><br>
<b>Figure 1</b>: Video camera V, suppliers, parts, envelopes and open source artifacts
</p>

Manufacturer M needs a way to trust that 1) each supplier has prepared the required compliance artifacts for their respective contribution; 2) in the event that an artifact was missing or not properly prepared (e.g., source code, legal notices, ...), we can identify who is responsible for remedying the situation; and 3) no one supplier can sabotage (hack) the integrity of the compliance artifacts of another supplier. We used the Blockchain technology to create a Software Parts Ledger to manage this complexity. It serves as a global data store that tracks the state of suppliers, their list of software parts, the corresponding envelopes and envelope content. Typical transactions performed on the Ledger include adding a part to a supplier’s parts list, assigning an envelope to a software part, and adding, updating and removing artifacts from an envelope.

<p align="center"><img src="./docs/images/blockchain-illustration.png" width="493" height="373"/>
<br><br>
<b>Figure 2</b>: Software Ledger </p>

Figure 2 illustrates Ledger entries that represent the parts for video camera V presented in Figure 2. Transactions 101 through 104 represent software part 37 and transactions 105 through 110 represent part 101. Transaction 111 illustrates that an additional artifact was later added to the part 37 envelope and transaction 112 illustrates that the source code was updated for part 101’s envelope. In the first instances, Supplier S1 forgot to include a notice artifact but was able to remedy it after the fact. In the second instance, Supplier S2 was able to determine that some of the mandatory/required source code was missing and to efficiently remedy the issue by executing another ledger transaction. By recording software part information in the ledger, customers of both suppliers S1 and S2 would automatically receive the updates. Upon shipping video camera V, manufacturer M could query the Ledger to obtain the latest most comprehensive collect of compliance artifacts available. If updates where made V's compliance envelope after it shipped (e.g., include missing source code) then manufacturer M and its customers would be able to obtain the latest version by referencing the Ledger. 

## Project Components

Our model of a supply chain network has two core system components: the **ledger** and **conductor**. The ledger tracks the relationships among suppliers, parts and corresponding compliance artifacts. The conductor is a background coordination process which, although optional, provides a number of useful services.

The **ledger**, built using the Hyperledger Project's Sawtooth platform, tracks:

- **suppliers** - providers of software parts. Each supplier must register with the ledger. 
- **software parts** - software parts used by manufactures to construct products - includes both simple and complex software parts. 
- **compliance artifacts** - artifacts prepared to satisfy the license obligations for the different opens source components used to create a software part. They typically include obligatory source code, written offers for source, license notices and/or copies of licenses. The collection could also include information that, although not required by a license, provides important utility, such as Open Source BOMs, SPDX licensing data and cryptography information.
- **compliance envelope** - a construct that represents a standard method of indexing, bundling and delivering the compliance artifacts as a single item. Regardless of whether a software offering is a simple atomic part (e.g., software library), or a more complex one such as the software runtime that controls a consumer device, the envelope contains a rich collection of information that represents all the open source parts that the offering was comprised of.
- **relationships** -  relationships between the above entities (e.g, supplier -> parts, part -> envelope, ...)

The ledger is accessible via a RESTful API, and python and go libraries. 

The **conductor** functions as the network's underlying kernel responsible for monitoring and coordinating the different supply chain network resources and entities (ledger, applications, suppliers, ...). For instance it maintains a directory of all the network suppliers, applications and ledger nodes. It serves up unique identifiers (UUID) for the various entities (e.g., suppliers, software parts, compliance envelopes, ...)  along with other supply chain network support services. The Conductor is accessible via a RESTful API. 

<p align="center"><img src="./docs/images/supplychain-network.png" width="547" height="399"/>
<br><br>
<b>Figure 3</b>: Supply Chain Network with core components: the ledger and conductor.
</p>

Figure 3 illustrates the relations between the suppliers, manufacture, software parts, compliance artifacts and customers. Suppliers register their software parts and compliance envelopes. 

The ledger provides the ability to maintain global state information across the supply chain network. This information established trust between suppliers and manufactures by holding suppliers accountable for their the open source compliance artifacts that accompany the software part delivery.

## Project License ##

The SParts project is licensed under the **Apache License, Version 2.0**. For further details, visit http://www.apache.org/licenses/LICENSE-2.0. All code created and/or contributed to the project is licensed under the Apache license. It may contain files under different licenses in the event code was borrowed from another open source project under a different license. Each source file should include a license notice that designates the licensing terms for the respective file. The license text for the SParts project can be found in the LICENSE file found in the project's top level directory. 

## Contributing ##
New source code contributions are made under the Apache-2.0 license and the contributor must sign off each commit under the [Developer Certificate of Origin (DCO) version 1.1](https://developercertificate.org).  To contribute or learn more about the project contact Mark.Gisi@WindRiver.com


## Legal Notices ##

All product names, logos, and brands are property of their respective owners. All company, product and service names used in this software are for identification purposes only. 

Disclaimer of Warranty / No Support: Wind River does not provide support and maintenance services for this software, under Wind River’s standard Software Support and Maintenance Agreement or otherwise. Unless required by applicable law, Wind River provides the software (and each contributor provides its contribution) on an “AS IS” BASIS, WITHOUT WARRANTIES OF ANY KIND, either express or implied, including, without limitation, any warranties of TITLE, NONINFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the software and assume any risks associated with your exercise of permissions under the license.


