from typing import Callable, List
from langchain.schema import (
    HumanMessage,
    SystemMessage,
)
from langchain_community.chat_models import ChatOllama

class DialogueAgent:
    def __init__(
        self,
        name: str,
        system_message: SystemMessage,
        model: ChatOllama,
    ) -> None:
        self.name = name
        self.system_message = system_message
        self.model = model
        self.prefix = f"{self.name}: "
        self.reset()

    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """
        message = self.model(
            [
                self.system_message,
                HumanMessage(content="\n".join(self.message_history + [self.prefix])),
            ]
        )
        return message.content

    def receive(self, name: str, message: str) -> None:
        """
        Concatenates {message} spoken by {name} into message history
        """
        self.message_history.append(f"{name}: {message}")

class DialogueSimulator:
    def __init__(
        self,
        agents: List[DialogueAgent],
        selection_function: Callable[[int, List[DialogueAgent]], int],
    ) -> None:
        self.agents = agents
        self._step = 0
        self.select_next_speaker = selection_function

    def reset(self):
        for agent in self.agents:
            agent.reset()

    def inject(self, name: str, message: str):
        """
        Initiates the conversation with a {message} from {name}
        """
        for agent in self.agents:
            agent.receive(name, message)

        # increment time
        self._step += 1

    def step(self) -> tuple[str, str]:
        # 1. choose the next speaker
        speaker_idx = self.select_next_speaker(self._step, self.agents)
        speaker = self.agents[speaker_idx]

        # 2. next speaker sends message
        message = speaker.send()

        # 3. everyone receives message
        for receiver in self.agents:
            receiver.receive(speaker.name, message)

        # 4. increment time
        self._step += 1

        return speaker.name, message




debatant_1_name = "Physicalist"
debatant_2_name = "Dualist"
debate_topic = "Debate the merits of physicalism"
word_limit = 20  # word limit for task brainstorming


debate_description = f"""Here is the topic for a debate: {debate_topic}.
        There are two participants in this debate: {debatant_1_name} and {debatant_2_name}."""

debatant_descriptor_system_message = SystemMessage(
    content="You can add detail to the description of a debatant."
)

debatant_1_specifier_prompt = [
    debatant_descriptor_system_message,
    HumanMessage(
        content=f"""{debate_description}
        Please reply with a creative description of the debatant {debatant_1_name}, in {word_limit} words or less.
        Speak directly to {debatant_1_name}.
        Do not add anything else."""
    ),
]
debatant_1_description = ChatOllama(temperature=1.0)(
    debatant_1_specifier_prompt
).content

debatant_2_specifier_prompt = [
    debatant_descriptor_system_message,
    HumanMessage(
        content=f"""{debate_description}
        Please reply with a creative description of the debatant {debatant_2_name}, in {word_limit} words or less.
        Speak directly to {debatant_2_name}.
        Do not add anything else."""
    ),
]
debatant_2_description = ChatOllama(temperature=1.0)(
    debatant_2_specifier_prompt
).content


debatant_1_system_message = SystemMessage(
    content=(
        f"""{debate_description}
Never forget you are the physicalist, {debatant_1_name}.
Your character description is as follows: {debatant_1_description}.
You will propose arguments in favor of physicalism.
Speak in the first person from the perspective of {debatant_1_name}.
Do not change roles!
Do not speak from the perspective of {debatant_2_name}.
Do not forget to finish speaking by saying, 'It is your turn, {debatant_2_name}.'
Do not add anything else.
Remember you are the physicalist, {debatant_1_name}.
Stop speaking the moment you finish speaking from your perspective.
"""
    )
)

debatant_2_system_message = SystemMessage(
    content=(
        f"""{debate_description}
Never forget you are the dualist, {debatant_2_name}.
Your character description is as follows: {debatant_2_description}.
You will propose arguments in favor of dualism.
Speak in the first person from the perspective of {debatant_2_name}.
Do not change roles!
Do not speak from the perspective of {debatant_1_name}.
Do not forget to finish speaking by saying, 'It is your turn, {debatant_1_name}.'
Do not add anything else.
Remember you are the dualist, {debatant_2_name}.
Stop speaking the moment you finish speaking from your perspective.
"""
    )
)

topic_specifier_prompt = [
    SystemMessage(content="You can make the topic of the debate more specific."),
    HumanMessage(
        content=f"""{debate_description}

        You are a neutral moderator of a debate between {debatant_2_name} and {debatant_1_name}.
        Please make the topic of the debate more specific. Be creative and imaginative.
        Please reply with the specified debate topic in {word_limit} words or less.
        Speak directly to the debatants {debatant_1_name} and {debatant_2_name}.
        Do not add anything else."""
    ),
]
specified_topic = ChatOllama(temperature=1.0)(topic_specifier_prompt).content




print(f"Original quest:\n{debate_topic}\n")
print(f"Detailed quest:\n{specified_topic}\n")

debatant_1 = DialogueAgent(
    name=debatant_1_name,
    system_message=debatant_1_system_message,
    model=ChatOllama(temperature=0.2),
)
debatant_2 = DialogueAgent(
    name=debatant_2_name,
    system_message=debatant_2_system_message,
    model=ChatOllama(temperature=0.2),
)

def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    idx = step % len(agents)
    return idx

max_iters = 4
n = 0

simulator = DialogueSimulator(
    agents=[debatant_1, debatant_2], selection_function=select_next_speaker
)
simulator.reset()
simulator.inject(debatant_2_name, specified_topic)
simulator.inject(debatant_1_name, specified_topic)
print(f"({debatant_2_name}): {specified_topic}")
print("\n")

while n < max_iters:
    name, message = simulator.step()
    print(f"({name}): {message}")
    print("\n")
    n += 1
