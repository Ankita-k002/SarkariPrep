import sqlite3
import os
from database import init_db, get_db_connection

# Define the seed questions
QUESTIONS = [
    # === UPSC Questions ===
    {
        "category": "UPSC",
        "subject": "Polity",
        "question_text": "With reference to the 'Basic Structure Doctrine' of the Indian Constitution, which of the following cases is considered its origin?",
        "option_a": "Golaknath v. State of Punjab (1967)",
        "option_b": "Kesavananda Bharati v. State of Kerala (1973)",
        "option_c": "Minerva Mills v. Union of India (1980)",
        "option_d": "Indira Gandhi v. Raj Narain (1975)",
        "correct_option": "B",
        "explanation": "The 'Basic Structure Doctrine' was propounded by the Supreme Court of India in the landmark Kesavananda Bharati v. State of Kerala case in 1973. The Court held that while Parliament has wide power to amend the Constitution under Article 368, it cannot amend or alter its 'basic structure' or essential features."
    },
    {
        "category": "UPSC",
        "subject": "Polity",
        "question_text": "Consider the following statements regarding the Governor of a State in India:\n1. The Governor can reserve certain bills passed by the State Legislature for the consideration of the President.\n2. The Governor has the constitutional discretion to appoint the Chief Minister when no single party gets a clear majority in the assembly.\nWhich of the statements given above is/are correct?",
        "option_a": "1 only",
        "option_b": "2 only",
        "option_c": "Both 1 and 2",
        "option_d": "Neither 1 nor 2",
        "correct_option": "C",
        "explanation": "Both statements are correct. Under Article 200, the Governor can reserve a bill passed by the state legislature for the President's consideration. Under discretionary powers, when no single party has a clear majority, the Governor exercises constitutional discretion to invite a leader to form the government."
    },
    {
        "category": "UPSC",
        "subject": "History",
        "question_text": "In the context of ancient Indian history, the term 'Agrahara' referred to which of the following?",
        "option_a": "Land granted to Brahmins, which was usually tax-free and carried the right to collect land revenue.",
        "option_b": "A royal treasury warehouse used for storing food grains during famines.",
        "option_c": "A fortified military administrative outpost during the Gupta period.",
        "option_d": "The assembly of merchants and traders in south Indian ports.",
        "correct_option": "A",
        "explanation": "An 'Agrahara' was a grant of land or an entire village given to Brahmins by kings and landlords in ancient and medieval India. These lands were typically tax-free, and the grantees were authorized to collect local taxes and maintain law and order."
    },
    {
        "category": "UPSC",
        "subject": "History",
        "question_text": "Which of the following statements best describes the principal objective of the Butler Committee (1927)?",
        "option_a": "Define the jurisdiction of the Central and Provincial Governments under the diarchy.",
        "option_b": "Improve the relationship between the Government of India and the Indian Princely States.",
        "option_c": "Suggest reforms in the judicial administration of British India.",
        "option_d": "Establish the framework for the introduction of civil services examinations in India.",
        "correct_option": "B",
        "explanation": "The Indian States Committee, popularly known as the Butler Committee, was appointed in 1927 to investigate and clarify the relationship between the British paramount power in India and the Indian Princely States, recommending measures for better economic and political integration."
    },
    {
        "category": "UPSC",
        "subject": "Geography",
        "question_text": "With reference to the Indian Ocean Dipole (IOD), which of the following statements is/are correct?\n1. The IOD phenomenon is characterized by a difference in sea surface temperatures between tropical Western Indian Ocean and tropical Eastern Indian Ocean.\n2. A positive IOD episode can lead to better monsoon rainfall in the Indian subcontinent.\nSelect the correct answer:",
        "option_a": "1 only",
        "option_b": "2 only",
        "option_c": "Both 1 and 2",
        "option_d": "Neither 1 nor 2",
        "correct_option": "C",
        "explanation": "Both statements are correct. The IOD is defined by the difference in sea surface temperature between the western pole (Arabian Sea) and the eastern pole (eastern Indian Ocean south of Indonesia). A positive IOD, marked by warmer waters in the western Indian Ocean, assists the Indian summer monsoon."
    },
    {
        "category": "UPSC",
        "subject": "Geography",
        "question_text": "Which of the following rivers originates from the Amarkantak plateau in Madhya Pradesh and flows towards the west?",
        "option_a": "Mahanadi",
        "option_b": "Narmada",
        "option_c": "Tapi",
        "option_d": "Godavari",
        "correct_option": "B",
        "explanation": "The Narmada River rises from the Amarkantak Hill range on the eastern edge of Madhya Pradesh. Unlike most peninsular rivers, it flows westward through a rift valley between the Vindhya and Satpura ranges and empties into the Arabian Sea."
    },
    {
        "category": "UPSC",
        "subject": "Economy",
        "question_text": "Which of the following measures is/are likely to reduce inflation in the Indian economy?\n1. Increase in the Cash Reserve Ratio (CRR) by the RBI.\n2. Sale of government securities in the Open Market Operations (OMO) by the RBI.\n3. Increase in public expenditure by the government.\nSelect the correct answer:",
        "option_a": "1 and 2 only",
        "option_b": "2 and 3 only",
        "option_c": "1 and 3 only",
        "option_d": "1, 2 and 3",
        "correct_option": "A",
        "explanation": "Increasing the CRR and selling government securities (OMO) drains liquidity from the banking system, reducing money supply and purchasing power, which helps curb inflation. Increasing public expenditure, on the other hand, injects money into the economy, which can increase demand and inflation."
    },
    {
        "category": "UPSC",
        "subject": "Economy",
        "question_text": "With reference to 'Capital Adequacy Ratio' (CAR), consider the following statements:\n1. It is the amount that banks have to maintain in the form of gold, cash, and government securities before lending.\n2. It is decided by each individual commercial bank independently to guard against bad loans.\nWhich of the statements given above is/are correct?",
        "option_a": "1 only",
        "option_b": "2 only",
        "option_c": "Both 1 and 2",
        "option_d": "Neither 1 nor 2",
        "correct_option": "D",
        "explanation": "Neither statement is correct. Capital Adequacy Ratio (CAR) is the ratio of a bank's capital to its risk-weighted assets, meant to protect depositors and promote financial stability. It is NOT maintained as liquid assets like gold/cash (that is SLR). Furthermore, CAR is mandated by the central bank (RBI, adhering to international Basel norms), not decided independently by commercial banks."
    },
    {
        "category": "UPSC",
        "subject": "Science",
        "question_text": "With reference to carbon nanotubes (CNTs), which of the following statements is/are correct?\n1. They can be used as carriers of drugs and antigens in the human body.\n2. They can be made into artificial blood capillaries for injured parts of the human body.\n3. They can be used in biochemical sensors.\n4. Carbon nanotubes are biodegradable.\nSelect the correct answer:",
        "option_a": "1, 2 and 3 only",
        "option_b": "2, 3 and 4 only",
        "option_c": "1, 3 and 4 only",
        "option_d": "1, 2, 3 and 4",
        "correct_option": "D",
        "explanation": "All four statements are correct regarding carbon nanotubes. Due to their unique mechanical, electrical, and structural properties, CNTs can act as drug delivery vectors, cell scaffolds (artificial capillaries), biochemical sensors, and studies have shown they can be biodegraded by certain enzymes like myeloperoxidase."
    },
    {
        "category": "UPSC",
        "subject": "Science",
        "question_text": "In the context of astronomical research, what is 'L1' in the Aditya-L1 solar mission of India?",
        "option_a": "The first Lunar orbit entry altitude.",
        "option_b": "The first Lagrangian point between Sun and Earth.",
        "option_c": "The launch pad designation at Sriharikota.",
        "option_d": "The low-gravity region of the Asteroid belt.",
        "correct_option": "B",
        "explanation": "L1 stands for Lagrange Point 1. It is a point in space where the gravitational forces of the Earth and the Sun, and the centrifugal force of the spacecraft's motion, balance out. This allows a spacecraft to remain in a stable position relative to the Earth and Sun with minimal fuel consumption, offering an uninterrupted view of the Sun."
    },
    {
        "category": "UPSC",
        "subject": "Current Affairs",
        "question_text": "India recently signed the 'Artemis Accords'. What is the primary focus of this international framework?",
        "option_a": "Global trade tariff regulations in digital services.",
        "option_b": "Cooperation in civil space exploration and peaceful utilization of the Moon, Mars, and other celestial bodies.",
        "option_c": "Joint military drills in the Indo-Pacific region.",
        "option_d": "Combating cross-border wildlife trafficking and deforestation in the Global South.",
        "correct_option": "B",
        "explanation": "The Artemis Accords are a non-binding multilateral arrangement between the US government and other world governments, including India. It is aimed at guiding civil space exploration and cooperation, establishing a safe, peaceful, and transparent framework for lunar and deep-space missions."
    },
    {
        "category": "UPSC",
        "subject": "Current Affairs",
        "question_text": "Which country hosted the G20 Leaders' Summit in September 2023, during which the African Union was admitted as a permanent member?",
        "option_a": "Indonesia",
        "option_b": "India",
        "option_c": "Brazil",
        "option_d": "South Africa",
        "correct_option": "B",
        "explanation": "India hosted the historic 18th G20 Summit in New Delhi on September 9-10, 2023. Under India's presidency, a major milestone was achieved when the African Union (AU) was formally admitted as a permanent member of the G20, matching the European Union's status."
    },
    {
        "category": "UPSC",
        "subject": "General Knowledge",
        "question_text": "Which of the following classical dance forms of India originates from the state of Kerala and is traditionally characterized by elaborate makeup and dramatic costumes?",
        "option_a": "Bharatanatyam",
        "option_b": "Kathakali",
        "option_c": "Kathak",
        "option_d": "Kuchipudi",
        "correct_option": "B",
        "explanation": "Kathakali is a major classical dance-drama from Kerala. It is renowned for its stylized makeup, massive colorful headdresses, elaborate costumes, and non-verbal storytelling using hand gestures (mudras) and facial expressions."
    },
    
    # === SSC Questions ===
    {
        "category": "SSC",
        "subject": "History",
        "question_text": "Who was the founder of the Maurya Empire in ancient India?",
        "option_a": "Ashoka the Great",
        "option_b": "Chandragupta Maurya",
        "option_c": "Bindusara",
        "option_d": "Chandragupta I",
        "correct_option": "B",
        "explanation": "Chandragupta Maurya founded the Maurya Empire in 322 BCE after defeating Dhanananda of the Nanda Dynasty with the administrative and strategic guidance of his chief advisor, Chanakya (Kautilya)."
    },
    {
        "category": "SSC",
        "subject": "History",
        "question_text": "The famous traveler Ibn Battuta visited India during the reign of which Delhi Sultan?",
        "option_a": "Alauddin Khalji",
        "option_b": "Muhammad bin Tughluq",
        "option_c": "Firoz Shah Tughluq",
        "option_d": "Ghiyasuddin Balban",
        "correct_option": "B",
        "explanation": "Ibn Battuta, the Moroccan explorer, arrived in India in 1333 CE during the rule of Muhammad bin Tughluq, who appointed him as a Qazi (judge) in Delhi due to his scholarly qualifications."
    },
    {
        "category": "SSC",
        "subject": "Geography",
        "question_text": "Which of the following is the highest peak in the Western Ghats (Sahyadri range) in India?",
        "option_a": "Doda Betta",
        "option_b": "Anamudi",
        "option_c": "Mahendragiri",
        "option_d": "Kalsubai",
        "correct_option": "B",
        "explanation": "Anamudi is the highest peak in the Western Ghats and in South India, with an elevation of 2,695 meters. It is located in the Ernakulam and Idukki districts of Kerala."
    },
    {
        "category": "SSC",
        "subject": "Geography",
        "question_text": "Which Indian state shares the longest international border with Bangladesh?",
        "option_a": "Assam",
        "option_b": "West Bengal",
        "option_c": "Tripura",
        "option_d": "Meghalaya",
        "correct_option": "B",
        "explanation": "West Bengal shares the longest border with Bangladesh among all Indian border states, stretching approximately 2,217 km out of the total 4,096 km India-Bangladesh border."
    },
    {
        "category": "SSC",
        "subject": "Polity",
        "question_text": "Which Article of the Indian Constitution is related to the 'Abolition of Untouchability'?",
        "option_a": "Article 14",
        "option_b": "Article 17",
        "option_c": "Article 19",
        "option_d": "Article 21",
        "correct_option": "B",
        "explanation": "Article 17 of the Constitution of India abolishes 'Untouchability' and forbids its practice in any form. The enforcement of any disability arising out of untouchability is a punishable offense in accordance with law."
    },
    {
        "category": "SSC",
        "subject": "Polity",
        "question_text": "Who appoints the Comptroller and Auditor General (CAG) of India?",
        "option_a": "Prime Minister of India",
        "option_b": "President of India",
        "option_c": "Chief Justice of India",
        "option_d": "Speaker of the Lok Sabha",
        "correct_option": "B",
        "explanation": "Under Article 148 of the Constitution, the Comptroller and Auditor General (CAG) of India is appointed by the President of India by warrant under his hand and seal."
    },
    {
        "category": "SSC",
        "subject": "Economy",
        "question_text": "Which institution regulates the stock markets (securities market) in India?",
        "option_a": "Reserve Bank of India (RBI)",
        "option_b": "Securities and Exchange Board of India (SEBI)",
        "option_c": "IRDAI",
        "option_d": "NABARD",
        "correct_option": "B",
        "explanation": "The Securities and Exchange Board of India (SEBI) is the regulatory body for securities and commodity markets in India, established under the SEBI Act, 1992, to protect investors and regulate market participants."
    },
    {
        "category": "SSC",
        "subject": "Science",
        "question_text": "What is the chemical name of common table salt?",
        "option_a": "Sodium carbonate",
        "option_b": "Sodium chloride",
        "option_c": "Sodium bicarbonate",
        "option_d": "Calcium chloride",
        "correct_option": "B",
        "explanation": "Common table salt is chemically known as Sodium Chloride (NaCl), formed by the ionic bonding of sodium and chlorine atoms."
    },
    {
        "category": "SSC",
        "subject": "Science",
        "question_text": "Which component of blood is primarily responsible for clotting at the site of an injury?",
        "option_a": "Red Blood Cells (RBCs)",
        "option_b": "Platelets (Thrombocytes)",
        "option_c": "White Blood Cells (WBCs)",
        "option_d": "Plasma",
        "correct_option": "B",
        "explanation": "Platelets, or thrombocytes, play a crucial role in blood clotting. When a blood vessel is damaged, platelets rush to the site, clump together to plug the leak, and release chemical factors to form a stable fibrin clot."
    },
    {
        "category": "SSC",
        "subject": "Current Affairs",
        "question_text": "Who was appointed as the 50th Chief Justice of India (CJI) in November 2022?",
        "option_a": "Justice U.U. Lalit",
        "option_b": "Justice D.Y. Chandrachud",
        "option_c": "Justice N.V. Ramana",
        "option_d": "Justice Sanjiv Khanna",
        "correct_option": "B",
        "explanation": "Justice Dhananjaya Yeshwant Chandrachud took oath as the 50th Chief Justice of India on November 9, 2022, succeeding Justice U.U. Lalit."
    },
    {
        "category": "SSC",
        "subject": "General Knowledge",
        "question_text": "The 'Lothal' archaeological site of the Indus Valley Civilization is located in which modern state of India?",
        "option_a": "Rajasthan",
        "option_b": "Gujarat",
        "option_c": "Haryana",
        "option_d": "Punjab",
        "correct_option": "B",
        "explanation": "Lothal, one of the most prominent cities of the ancient Indus Valley Civilization, known for its massive tidal dockyard, is situated in the Bhal region of modern-day Gujarat."
    },

    # === Banking Questions ===
    {
        "category": "Banking",
        "subject": "Economy",
        "question_text": "What is the term used for the interest rate at which the Reserve Bank of India (RBI) borrows money from commercial banks in the short term?",
        "option_a": "Repo Rate",
        "option_b": "Reverse Repo Rate",
        "option_c": "Bank Rate",
        "option_d": "Marginal Standing Facility (MSF) Rate",
        "correct_option": "B",
        "explanation": "The Reverse Repo Rate is the rate at which the RBI borrows funds from commercial banks. Banks park their excess funds with the RBI using this window to earn interest. Increasing this rate incentivizes banks to hold money with the RBI, reducing market liquidity."
    },
    {
        "category": "Banking",
        "subject": "Economy",
        "question_text": "What does the abbreviation 'NPA' stand for in banking terms?",
        "option_a": "Net Profit Assets",
        "option_b": "Non-Performing Assets",
        "option_c": "National Payment Association",
        "option_d": "Nominal Prime Account",
        "correct_option": "B",
        "explanation": "NPA stands for Non-Performing Asset. It is a loan or advance for which the principal or interest payment remains overdue for a period of 90 days or more, indicating a default risk."
    },
    {
        "category": "Banking",
        "subject": "General Knowledge",
        "question_text": "In which city is the headquarters of the Asian Development Bank (ADB) located?",
        "option_a": "Tokyo, Japan",
        "option_b": "Manila (Mandaluyong), Philippines",
        "option_c": "Beijing, China",
        "option_d": "Singapore",
        "correct_option": "B",
        "explanation": "The Asian Development Bank (ADB), established in 1966 to foster economic development in Asia, has its headquarters located in Metro Manila, Philippines."
    },
    {
        "category": "Banking",
        "subject": "Polity",
        "question_text": "Which committee recommended the establishment of Regional Rural Banks (RRBs) in India?",
        "option_a": "Narasimham Committee",
        "option_b": "M. Narasimham Working Group (1975)",
        "option_c": "Hilton Young Commission",
        "option_d": "Urjit Patel Committee",
        "correct_option": "B",
        "explanation": "The establishment of Regional Rural Banks (RRBs) was recommended by the Narasimham Committee on Rural Credit (Working Group under M. Narasimham) in 1975, leading to the RRB Act of 1976."
    },
    {
        "category": "Banking",
        "subject": "Science",
        "question_text": "Which technology forms the underlying foundation of Cryptocurrencies and is being explored by banking sectors for secure, decentralized ledger transactions?",
        "option_a": "Artificial Intelligence",
        "option_b": "Blockchain",
        "option_c": "Cloud Computing",
        "option_d": "Virtual Reality",
        "correct_option": "B",
        "explanation": "Blockchain technology is a decentralized, distributed ledger that records the provenance of a digital asset. Its cryptographic hashing and consensus mechanisms make it highly secure and tamper-proof, attracting banking institutions for transaction logs."
    },
    {
        "category": "Banking",
        "subject": "Current Affairs",
        "question_text": "What is the name of the Central Bank Digital Currency (CBDC) introduced by the RBI for retail users on a pilot basis?",
        "option_a": "e-Gold",
        "option_b": "Digital Rupee (e₹-R)",
        "option_c": "UPI Cash",
        "option_d": "Bharat Coin",
        "correct_option": "B",
        "explanation": "The Reserve Bank of India (RBI) launched pilot runs for its Central Bank Digital Currency, known as the Digital Rupee (e-Rupee or e₹), representing a digital token format of legal tender."
    },

    # === Railways Questions ===
    {
        "category": "Railways",
        "subject": "General Knowledge",
        "question_text": "In which year was the first passenger train run in India between Bori Bunder (Bombay) and Thane?",
        "option_a": "1850",
        "option_b": "1853",
        "option_c": "1857",
        "option_d": "1862",
        "correct_option": "B",
        "explanation": "The first commercial passenger train in India ran on April 16, 1853, between Bori Bunder in Bombay and Thane, covering a distance of 34 kilometers with 400 passengers across 14 carriages."
    },
    {
        "category": "Railways",
        "subject": "Geography",
        "question_text": "Where is the headquarters of the Southern Railway Zone of Indian Railways located?",
        "option_a": "Secunderabad",
        "option_b": "Chennai",
        "option_c": "Kolkata",
        "option_d": "Bengaluru",
        "correct_option": "B",
        "explanation": "The Southern Railway Zone, one of the earliest zones created in Indian Railways (1951), has its headquarters located at Chennai Central, Tamil Nadu."
    },
    {
        "category": "Railways",
        "subject": "Science",
        "question_text": "Which physical law explains why passengers in a moving train jerk forward when the brakes are applied suddenly?",
        "option_a": "Newton's First Law of Motion (Inertia)",
        "option_b": "Newton's Second Law of Motion",
        "option_c": "Newton's Third Law of Motion",
        "option_d": "Law of Conservation of Momentum",
        "correct_option": "A",
        "explanation": "Newton's First Law (Law of Inertia) states that an object remains in a state of rest or uniform motion unless acted upon by an external force. When a train stops, the passengers' lower bodies stop with the train, while their upper bodies continue moving forward due to inertia of motion."
    },
    {
        "category": "Railways",
        "subject": "Polity",
        "question_text": "Which constitutional amendment or report recommended the merger of the Railway Budget back into the General Union Budget of India in 2017?",
        "option_a": "Debroy Committee report",
        "option_b": "Bibek Debroy Committee report (2015)",
        "option_c": "Acworth Committee report (1924)",
        "option_d": "Kothari Commission",
        "correct_option": "B",
        "explanation": "Following the recommendations of the Committee headed by Bibek Debroy (Member, NITI Aayog), the government decided to merge the 92-year-old separate Railway Budget with the Union General Budget starting from the fiscal year 2017-18."
    },

    # === State PSC Questions ===
    {
        "category": "State PSC",
        "subject": "History",
        "question_text": "The historic Battle of Buxar was fought in which year, paving the way for British administrative dominance in Bengal, Bihar, and Odisha?",
        "option_a": "1757",
        "option_b": "1764",
        "option_c": "1772",
        "option_d": "1784",
        "correct_option": "B",
        "explanation": "The Battle of Buxar was fought on October 22, 1764, between the British East India Company forces led by Hector Munro and the combined allied forces of Mir Qasim (Nawab of Bengal), Shuja-ud-Daula (Nawab of Awadh), and Shah Alam II (Mughal Emperor)."
    },
    {
        "category": "State PSC",
        "subject": "Geography",
        "question_text": "The 'Indira Gandhi Canal', one of the largest canal systems in India, primarily draws its water from which of the following rivers?",
        "option_a": "Ganga and Yamuna",
        "option_b": "Sutlej and Beas",
        "option_c": "Jhelum and Chenab",
        "option_d": "Chambal and Narmada",
        "correct_option": "B",
        "explanation": "The Indira Gandhi Canal starts from the Harike Barrage at the confluence of the Sutlej and Beas rivers in Punjab, bringing green irrigation lines to the arid Thar Desert region of Rajasthan."
    },
    {
        "category": "State PSC",
        "subject": "Polity",
        "question_text": "Under the 73rd Constitutional Amendment Act, what is the minimum age prescribed for contesting elections to Panchayat bodies?",
        "option_a": "18 years",
        "option_b": "21 years",
        "option_c": "25 years",
        "option_d": "30 years",
        "correct_option": "B",
        "explanation": "While the voting age is 18, Article 243-F of the Indian Constitution prescribes that a person must have attained the age of 21 years to contest local body elections (Panchayats and Municipalities)."
    },

    # === General / Generic Questions ===
    {
        "category": "General",
        "subject": "General Knowledge",
        "question_text": "Which of the following books was written by the ancient Indian scholar Chanakya?",
        "option_a": "Indica",
        "option_b": "Arthashastra",
        "option_c": "Mudrarakshasa",
        "option_d": "Rajatarangini",
        "correct_option": "B",
        "explanation": "The Arthashastra is an ancient Indian Sanskrit treatise on statecraft, economic policy, and military strategy, authored by Chanakya (also known as Kautilya or Vishnugupta)."
    },
    {
        "category": "General",
        "subject": "Science",
        "question_text": "Which gas is most abundant in the Earth's atmosphere?",
        "option_a": "Oxygen",
        "option_b": "Nitrogen",
        "option_c": "Carbon dioxide",
        "option_d": "Argon",
        "correct_option": "B",
        "explanation": "Nitrogen makes up approximately 78% of the Earth's atmosphere, followed by Oxygen at about 21%, Argon at 0.93%, and trace amounts of other gases including Carbon Dioxide."
    },
    {
        "category": "General",
        "subject": "History",
        "question_text": "In which city did Mahatma Gandhi launch his first satyagraha movement in India in 1917?",
        "option_a": "Champaran, Bihar",
        "option_b": "Kheda, Gujarat",
        "option_c": "Ahmedabad, Gujarat",
        "option_d": "Bardoli, Gujarat",
        "correct_option": "A",
        "explanation": "The Champaran Satyagraha of 1917 in Bihar was the first satyagraha movement led by Mahatma Gandhi in India. It was a protest against the oppressive tinkathia system, where tenant farmers were forced to grow indigo."
    },
    {
        "category": "General",
        "subject": "Geography",
        "question_text": "Which strait separates India and Sri Lanka?",
        "option_a": "Malacca Strait",
        "option_b": "Palk Strait",
        "option_c": "Sundar Strait",
        "option_d": "Hormuz Strait",
        "correct_option": "B",
        "explanation": "The Palk Strait is a strait between the Tamil Nadu state of India and the Mannar district of the Northern Province of Sri Lanka. It connects the Bay of Bengal in the northeast with the Palk Bay in the southwest."
    },
    {
        "category": "General",
        "subject": "Polity",
        "question_text": "Who is the ex-officio Chairman of the Rajya Sabha (Upper House of Indian Parliament)?",
        "option_a": "President of India",
        "option_b": "Vice-President of India",
        "option_c": "Prime Minister of India",
        "option_d": "Speaker of Lok Sabha",
        "correct_option": "B",
        "explanation": "Article 64 of the Indian Constitution mandates that the Vice-President of India shall be the ex-officio Chairman of the Council of States (Rajya Sabha)."
    },
    {
        "category": "General",
        "subject": "Economy",
        "question_text": "What is the primary indicator used to measure inflation in India for policy decisions by the RBI Monetary Policy Committee?",
        "option_a": "Wholesale Price Index (WPI)",
        "option_b": "Consumer Price Index (CPI) - Combined",
        "option_c": "Gross Domestic Product (GDP) Deflator",
        "option_d": "Index of Industrial Production (IIP)",
        "correct_option": "B",
        "explanation": "The RBI uses the Consumer Price Index (CPI) - Combined (headline inflation) as its key gauge of inflation for monetary policymaking, following reforms initiated in 2014."
    },
    {
        "category": "General",
        "subject": "Current Affairs",
        "question_text": "In which city was the world's largest meditation center, 'Swarved Mahamandir', inaugurated in December 2023?",
        "option_a": "Haridwar",
        "option_b": "Varanasi",
        "option_c": "Rishikesh",
        "option_d": "Ujjain",
        "correct_option": "B",
        "explanation": "Prime Minister Narendra Modi inaugurated the Swarved Mahamandir, the world's largest meditation center, at Umaraha in Varanasi, Uttar Pradesh. It can accommodate 20,000 people at once for meditation."
    }
]

# Additional generated questions to expand seed collection to cover all categories and subjects
CATEGORIES = ['General', 'UPSC', 'SSC', 'Banking', 'Railways', 'State PSC']
SUBJECTS = ['History', 'Geography', 'Polity', 'Economy', 'Science', 'Current Affairs', 'General Knowledge']

def generate_extended_questions():
    # We will generate a base set of templates and distribute them across combinations
    extra_questions = []
    
    # Let's add questions to reach a substantial set (~150 questions)
    # Template index to generate variation
    idx = 0
    for category in CATEGORIES:
        for subject in SUBJECTS:
            # Check if we already have questions for this combination in our core seed
            existing = [q for q in QUESTIONS if q["category"] == category and q["subject"] == subject]
            needed = 4 - len(existing) # Seed 4 questions per combination
            
            for k in range(needed):
                idx += 1
                q_text = f"[{category} Exam Specimen] Which of the following is correct regarding {subject} topic model questions (Type {idx})?"
                opt_a = f"Standard concept definition related to {subject} Type A"
                opt_b = f"Advanced operational mechanism of {subject} Type B"
                opt_c = f"Historically verified statement about {subject} Type C"
                opt_d = f"Chronologically recorded fact on {subject} Type D"
                correct = ["A", "B", "C", "D"][idx % 4]
                explanation = f"This is a sample seed question designed to provide study coverage for the '{category}' exam in the subject area of '{subject}'. The correct option is {correct} because of standard guidelines and official syllabus provisions for government exam syllabus revision."
                
                # Replace with more realistic questions for the database!
                # Let's curate some actual templates:
                if subject == "History":
                    q_text = f"Regarding {category} preparation: In which year was the Indian National Congress (INC) founded by A.O. Hume?"
                    opt_a = "1885"
                    opt_b = "1890"
                    opt_c = "1905"
                    opt_d = "1915"
                    correct = "A"
                    explanation = "The Indian National Congress (INC) was founded in December 1885 in Bombay by retired civil servant Allan Octavian Hume, along with leaders like Dinshaw Wacha and Dadabhai Naoroji."
                elif subject == "Polity":
                    q_text = f"For {category} General Studies: Which schedule of the Indian Constitution is related to 'Anti-Defection' laws?"
                    opt_a = "Eighth Schedule"
                    opt_b = "Ninth Schedule"
                    opt_c = "Tenth Schedule"
                    opt_d = "Eleventh Schedule"
                    correct = "C"
                    explanation = "The Tenth Schedule of the Constitution, popularly known as the Anti-Defection Law, was added by the 52nd Amendment Act of 1985 to prevent political defections."
                elif subject == "Geography":
                    q_text = f"Which of the following soils is also known as 'Regur Soil' and is ideal for growing cotton in India?"
                    opt_a = "Alluvial Soil"
                    opt_b = "Black Soil"
                    opt_c = "Red Soil"
                    opt_d = "Laterite Soil"
                    correct = "B"
                    explanation = "Black soil, commonly known as Regur soil or black cotton soil, is highly argillaceous, moisture-retentive, and rich in nutrients, making it perfect for cotton cultivation. It is found extensively in the Deccan trap region."
                elif subject == "Economy":
                    q_text = f"What is the term used for the simultaneous occurrence of low economic growth and high inflation?"
                    opt_a = "Deflation"
                    opt_b = "Stagflation"
                    opt_c = "Reflation"
                    opt_d = "Hyperinflation"
                    correct = "B"
                    explanation = "Stagflation is an economic condition characterized by slow economic growth, high unemployment (stagnation), accompanied by rising prices (inflation)."
                elif subject == "Science":
                    q_text = f"Which cell organelle is famously known as the 'Powerhouse of the Cell'?"
                    opt_a = "Nucleus"
                    opt_b = "Mitochondria"
                    opt_c = "Ribosome"
                    opt_d = "Golgi Apparatus"
                    correct = "B"
                    explanation = "Mitochondria are known as the powerhouses of the cell because they generate most of the cell's supply of adenosine triphosphate (ATP), used as a source of chemical energy."
                elif subject == "Current Affairs":
                    q_text = f"For the upcoming {category} exam: Which Indian state's tableaus won the first prize in the Republic Day Parade 2024?"
                    opt_a = "Uttar Pradesh"
                    opt_b = "Odisha"
                    opt_c = "Gujarat"
                    opt_d = "Maharashtra"
                    correct = "B"
                    explanation = "Odisha's tableau, themed 'Women Empowerment in Viksit Bharat', won the first prize among state tableaus in the Republic Day Parade 2024."
                else: # General Knowledge
                    q_text = f"Which is the longest river in the world?"
                    opt_a = "Amazon River"
                    opt_b = "Nile River"
                    opt_c = "Yangtze River"
                    opt_d = "Mississippi River"
                    correct = "B"
                    explanation = "The Nile River, stretching approximately 6,650 kilometers (4,132 miles) through northeastern Africa, is traditionally considered the longest river in the world, though some studies suggest the Amazon is longer."
                
                extra_questions.append({
                    "category": category,
                    "subject": subject,
                    "question_text": q_text,
                    "option_a": opt_a,
                    "option_b": opt_b,
                    "option_c": opt_c,
                    "option_d": opt_d,
                    "correct_option": correct,
                    "explanation": explanation
                })
                
    return extra_questions

def main():
    print("Initializing Database...")
    init_db()
    
    print("Database Initialized. Seeding Core Questions...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing questions just in case to prevent duplicates on re-run
    cursor.execute("DELETE FROM questions")
    
    # Insert Core Questions
    for q in QUESTIONS:
        cursor.execute('''
        INSERT INTO questions 
        (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai_generated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (q["category"], q["subject"], q["question_text"], q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_option"], q["explanation"]))
        
    # Generate and Insert Extended Questions
    print("Generating and seeding extended questions to cover syllabus...")
    extended = generate_extended_questions()
    for q in extended:
        cursor.execute('''
        INSERT INTO questions 
        (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai_generated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (q["category"], q["subject"], q["question_text"], q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_option"], q["explanation"]))
        
    conn.commit()
    
    # Check question count
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    print(f"Seeding completed successfully! Total questions in database: {count}")
    
    conn.close()

if __name__ == '__main__':
    main()
