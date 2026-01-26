import {
  Html,
  Body,
  Container,
  Text,
  Link,
  Button,
  Heading,
  Tailwind,
  Section, // Added Section for better layout
} from '@react-email/components';
import * as React from 'react';

interface MentionNotificationEmailProps {
  mentionedBy: string;
  ticketId: string;
  ticketSubject: string;
  commentText: string;
  dashboardUrl: string;
}

export const MentionNotificationEmail: React.FC<Readonly<MentionNotificationEmailProps>> = ({
  mentionedBy,
  ticketId,
  ticketSubject,
  commentText,
  dashboardUrl,
}) => {
  const ticketUrl = `${dashboardUrl}/support?ticketId=${ticketId}`;

  return (
    <Html>
      <Tailwind>
        <Body className="bg-gray-100 p-5 font-sans">
          <Container className="bg-white border border-gray-200 rounded-lg p-5 max-w-xl mx-auto">
            <Heading className="text-2xl font-bold text-gray-800 my-0">
              Nouvelle Mention sur KlandoDash
            </Heading>

            <Section className="mt-5">
              <Text className="text-base leading-relaxed text-gray-700">
                Bonjour,
              </Text>
              <Text className="text-base leading-relaxed text-gray-700">
                <strong className="font-bold">{mentionedBy}</strong> vous a mentionné dans un commentaire sur le ticket : <strong className="font-bold">"{ticketSubject}"</strong>.
              </Text>
            </Section>

            <Section className="border-l-4 border-gray-300 pl-4 my-5 text-gray-600 italic">
              <Text className="my-0">"{commentText}"</Text>
            </Section>

            <Section>
              <Text className="text-base leading-relaxed text-gray-700">
                Vous pouvez consulter le commentaire et répondre en cliquant sur le bouton ci-dessous :
              </Text>
              <Button
                href={ticketUrl}
                className="inline-block px-5 py-3 bg-red-700 text-white font-bold rounded-md text-base text-center no-underline mt-5" // Using a Tailwind class that should map to klando-burgundy
              >
                Voir le Ticket
              </Button>
            </Section>

            <Section className="mt-5 text-xs text-gray-500 text-center">
              <Text>
                Cet e-mail est une notification automatique. Merci de ne pas y répondre.
              </Text>
            </Section>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};