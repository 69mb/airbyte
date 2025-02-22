import React, { Suspense, useEffect, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import HeadTitle from "components/HeadTitle";
import { useCreateSource, useSourceList } from "hooks/services/useSourceHook";
import {
  useCreateDestination,
  useDestinationList,
} from "hooks/services/useDestinationHook";
import {
  useConnectionList,
  useSyncConnection,
} from "hooks/services/useConnectionHook";
import { ConnectionConfiguration } from "core/domain/connection";
import useGetStepsConfig from "./useStepsConfig";
import SourceStep from "./components/SourceStep";
import DestinationStep from "./components/DestinationStep";
import ConnectionStep from "./components/ConnectionStep";
import WelcomeStep from "./components/WelcomeStep";
import FinalStep from "./components/FinalStep";
import LetterLine from "./components/LetterLine";
import { StepType } from "./types";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import StepsCounter from "./components/StepsCounter";
import LoadingPage from "components/LoadingPage";
import useWorkspace from "hooks/services/useWorkspace";
import useRouterHook from "hooks/useRouter";
import { JobInfo } from "core/domain/job";
import { RoutePaths } from "../routePaths";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

const Content = styled.div<{ big?: boolean; medium?: boolean }>`
  width: 100%;
  max-width: ${({ big, medium }) => (big ? 1140 : medium ? 730 : 550)}px;
  margin: 0 auto;
  padding: 75px 0 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100%;
  position: relative;
  z-index: 2;
`;

const Footer = styled.div`
  width: 100%;
  height: 100px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px 0;
`;

const ScreenContent = styled.div`
  width: 100%;
  position: relative;
`;

const OnboardingPage: React.FC = () => {
  const analyticsService = useAnalyticsService();
  const { push } = useRouterHook();

  useEffect(() => {
    analyticsService.page("Onboarding Page");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const { sources } = useSourceList();
  const { destinations } = useDestinationList();
  const { connections } = useConnectionList();
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const { mutateAsync: syncConnection } = useSyncConnection();

  const { mutateAsync: createSource } = useCreateSource();
  const { mutateAsync: createDestination } = useCreateDestination();
  const { finishOnboarding } = useWorkspace();

  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
    message: string;
  } | null>(null);

  const afterUpdateStep = () => {
    setSuccessRequest(false);
    setErrorStatusRequest(null);
  };

  const { currentStep, setCurrentStep, steps } = useGetStepsConfig(
    !!sources.length,
    !!destinations.length,
    !!connections.length,
    afterUpdateStep
  );

  const handleFinishOnboarding = () => {
    finishOnboarding();
    push(RoutePaths.Connections);
  };

  const renderStep = () => {
    if (currentStep === StepType.INSTRUCTION) {
      const onStart = () => setCurrentStep(StepType.CREATE_SOURCE);
      //TODO: add username
      return <WelcomeStep onSubmit={onStart} userName="" />;
    }
    if (currentStep === StepType.CREATE_SOURCE) {
      const getSourceDefinitionById = (id: string) =>
        sourceDefinitions.find((item) => item.sourceDefinitionId === id);

      const onSubmitSourceStep = async (values: {
        name: string;
        serviceType: string;
        sourceId?: string;
        connectionConfiguration?: ConnectionConfiguration;
      }) => {
        setErrorStatusRequest(null);
        const sourceConnector = getSourceDefinitionById(values.serviceType);

        try {
          await createSource({ values, sourceConnector });

          setSuccessRequest(true);
          setTimeout(() => {
            setSuccessRequest(false);
            setCurrentStep(StepType.CREATE_DESTINATION);
          }, 2000);
        } catch (e) {
          setErrorStatusRequest(e);
        }
      };
      return (
        <SourceStep
          afterSelectConnector={() => setErrorStatusRequest(null)}
          onSubmit={onSubmitSourceStep}
          availableServices={sourceDefinitions}
          hasSuccess={successRequest}
          error={errorStatusRequest}
        />
      );
    }
    if (currentStep === StepType.CREATE_DESTINATION) {
      const getDestinationDefinitionById = (id: string) =>
        destinationDefinitions.find(
          (item) => item.destinationDefinitionId === id
        );

      const onSubmitDestinationStep = async (values: {
        name: string;
        serviceType: string;
        destinationDefinitionId?: string;
        connectionConfiguration?: ConnectionConfiguration;
      }) => {
        setErrorStatusRequest(null);
        const destinationConnector = getDestinationDefinitionById(
          values.serviceType
        );

        try {
          await createDestination({
            values,
            destinationConnector,
          });

          setSuccessRequest(true);
          setTimeout(() => {
            setSuccessRequest(false);
            setCurrentStep(StepType.SET_UP_CONNECTION);
          }, 2000);
        } catch (e) {
          setErrorStatusRequest(e);
        }
      };
      return (
        <DestinationStep
          afterSelectConnector={() => setErrorStatusRequest(null)}
          onSubmit={onSubmitDestinationStep}
          availableServices={destinationDefinitions}
          hasSuccess={successRequest}
          error={errorStatusRequest}
        />
      );
    }

    if (currentStep === StepType.SET_UP_CONNECTION) {
      return (
        <ConnectionStep
          errorStatus={errorStatusRequest?.status}
          source={sources[0]}
          destination={destinations[0]}
          afterSubmitConnection={() => setCurrentStep(StepType.FINAl)}
        />
      );
    }

    const onSync = () => syncConnection(connections[0]);

    return (
      <FinalStep connectionId={connections[0].connectionId} onSync={onSync} />
    );
  };

  return (
    <ScreenContent>
      {currentStep === StepType.CREATE_SOURCE ? (
        <LetterLine exit={successRequest} />
      ) : currentStep === StepType.CREATE_DESTINATION ? (
        <LetterLine onRight exit={successRequest} />
      ) : null}
      <Content
        big={currentStep === StepType.SET_UP_CONNECTION}
        medium={
          currentStep === StepType.INSTRUCTION || currentStep === StepType.FINAl
        }
      >
        <HeadTitle titles={[{ id: "onboarding.headTitle" }]} />
        <StepsCounter steps={steps} currentStep={currentStep} />

        <Suspense fallback={<LoadingPage />}>{renderStep()}</Suspense>

        <Footer>
          <Button secondary onClick={() => handleFinishOnboarding()}>
            {currentStep === StepType.FINAl ? (
              <FormattedMessage id="onboarding.closeOnboarding" />
            ) : (
              <FormattedMessage id="onboarding.skipOnboarding" />
            )}
          </Button>
        </Footer>
      </Content>
    </ScreenContent>
  );
};

export default OnboardingPage;
